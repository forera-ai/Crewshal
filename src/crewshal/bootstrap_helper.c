/* Owned Linux bootstrap helper. Source preparation only; no installed executable.
 * Compile and qualify exact helper/libc bytes only in a separately gated batch.
 * Namespace, role, storage, cgroup and credential setup belong to trusted setup.
 */
#define _GNU_SOURCE
#if !defined(__linux__)
#error "Crewshal bootstrap requires Linux"
#endif
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <poll.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/prctl.h>
#include <sys/ptrace.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/timerfd.h>
#include <time.h>
#include <unistd.h>

extern char **environ;

/* Normalize explicitly passed descriptors after Popen's exec handshake, never
 * from a Python preexec callback. Duplicate every input before replacing any
 * destination, so overlapping source/destination numbers cannot alias controls.
 * A failure refuses; the owning parent retains recovery responsibility.
 */
static int control_fds(char **numbers, int count, int namespace_setup) {
    int original[5], retained[5];
    struct stat st;
    for (int i = 0; i < count; ++i) {
        char *end;
        errno = 0;
        long value = strtol(numbers[i], &end, 10);
        if (errno || !numbers[i][0] || *end || value < 3 || value > INT_MAX)
            return 125;
        original[i] = (int)value;
        for (int j = 0; j < i; ++j) if (original[j] == original[i]) return 125;
        if (fstat(original[i], &st)) return 125;
        if (namespace_setup) {
            if (i == 0) {
                int seals = F_SEAL_WRITE | F_SEAL_GROW | F_SEAL_SHRINK | F_SEAL_SEAL;
                if (!S_ISREG(st.st_mode) || st.st_size <= 0 || st.st_size > 262144 ||
                    fcntl(original[i], F_GET_SEALS) != seals) return 125;
            } else if (!S_ISDIR(st.st_mode)) return 125;
        } else {
            int expected = i == 0 ? (O_WRONLY | O_NONBLOCK) :
                           i == 1 ? O_RDONLY : (O_WRONLY | O_NONBLOCK);
            if ((i == 0 ? !S_ISREG(st.st_mode) : !S_ISFIFO(st.st_mode)) ||
                (fcntl(original[i], F_GETFL) & (O_ACCMODE | O_NONBLOCK)) != expected)
                return 125;
        }
    }
    for (int i = 0; i < count; ++i) {
        retained[i] = fcntl(original[i], F_DUPFD_CLOEXEC, 16);
        if (retained[i] < 0) return 125;
    }
    for (int i = 0; i < count; ++i)
        if (dup2(retained[i], i + 3) != i + 3) return 125;
    if (syscall(SYS_close_range, (unsigned)(count + 3), ~0U, 0U) < 0) return 125;
    return 0;
}

static int kill_owned_worker(void) {
    /* FD 3 is a retained, independently verified owned cgroup.kill interface.
     * Never reopen a path or signal a numeric PID here.
     */
    ssize_t n;
    do { n = write(3, "1", 1); } while (n < 0 && errno == EINTR);
    return n == 1 ? 0 : 125;
}

static int watchdog(void) {
    /* Trusted launcher supplies: 3 kill, 4 parent lifeline, 5 readiness writer.
     * It must keep this process in the supervisor role, outside the worker.
     * Closing the lifeline never disarms the deadline: it kills the worker.
     */
    struct stat st;
    if (fstat(3, &st) || !S_ISREG(st.st_mode) ||
        (fcntl(3, F_GETFL) & (O_ACCMODE | O_NONBLOCK)) != (O_WRONLY | O_NONBLOCK) ||
        fstat(4, &st) || !S_ISFIFO(st.st_mode) ||
        (fcntl(4, F_GETFL) & O_ACCMODE) != O_RDONLY ||
        fstat(5, &st) || !S_ISFIFO(st.st_mode) ||
        (fcntl(5, F_GETFL) & (O_ACCMODE | O_NONBLOCK)) != (O_WRONLY | O_NONBLOCK))
        return 125;
    /* Avoid an inherited SIGPIPE terminating readiness failure before cleanup. */
    if (signal(SIGPIPE, SIG_IGN) == SIG_ERR) { kill_owned_worker(); return 125; }
    if (syscall(SYS_close_range, 6U, ~0U, 0U) < 0) {
        kill_owned_worker(); return 125;
    }
    struct timespec origin;
    if (clock_gettime(CLOCK_MONOTONIC, &origin)) {
        kill_owned_worker(); return 125;
    }
    int timer = timerfd_create(CLOCK_MONOTONIC, TFD_CLOEXEC | TFD_NONBLOCK);
    /* Exact armed checkpoint reserves FD 6 for independent timerfd readback.
     * Missing stdio or a changed descriptor layout refuses before readiness.
     */
    if (timer != 6) { kill_owned_worker(); return 125; }
    struct itimerspec limit = {0};
    limit.it_value = origin;
    limit.it_value.tv_sec += 5;
    if (timerfd_settime(timer, TFD_TIMER_ABSTIME, &limit, NULL)) {
        kill_owned_worker(); return 125;
    }
    uint64_t start = (uint64_t)origin.tv_sec * 1000000000ULL + (uint64_t)origin.tv_nsec;
    char ready[80];
    int length = snprintf(ready, sizeof ready, "READY %llu %llu\n",
                         (unsigned long long)start,
                         (unsigned long long)(start + 5000000000ULL));
    ssize_t written;
    do { written = write(5, ready, (size_t)length); } while (written < 0 && errno == EINTR);
    close(5);
    if (written != length) { kill_owned_worker(); return 125; }
    struct pollfd events[2] = {{timer, POLLIN, 0}, {4, POLLIN, 0}};
    int result;
    do { result = poll(events, 2, -1); } while (result < 0 && errno == EINTR);
    /* Expiry, parent loss, unexpected input and any observer error all stop. */
    int stopped = kill_owned_worker();
    close(timer);
    close(4);
    close(3);
    return result > 0 && stopped == 0 ? 0 : 125;
}

int main(int argc, char **argv) {
    if (argc == 5 && strcmp(argv[1], "--watchdog-fds") == 0) {
        if (control_fds(argv + 2, 3, 0)) return 125;
        /* Re-exec establishes the existing exact armed argv checkpoint. */
        char *command[] = {"/bin/crewshal-bootstrap", "--watchdog", NULL};
        execve(command[0], command, environ);
        return 125;
    }
    if (argc >= 10 && strcmp(argv[1], "--namespace-fds") == 0) {
        if (strcmp(argv[7], "--") || strcmp(argv[8], "/usr/bin/bwrap") ||
            control_fds(argv + 2, 5, 1)) return 125;
        execve(argv[8], argv + 8, environ);
        return 125;
    }
    if (argc == 2 && strcmp(argv[1], "--watchdog") == 0) return watchdog();
    if (argc < 4 || strcmp(argv[1], "--exec") != 0 ||
        strcmp(argv[2], "/opt/codex/bin/codex") != 0) return 125;
    pid_t parent = getppid();
    if (parent <= 1 || prctl(PR_SET_PDEATHSIG, SIGKILL) || getppid() != parent) return 125;
    if (chdir("/scratch/checkout") || syscall(SYS_close_range, 3U, ~0U, 0U) < 0) return 125;
    /* Helper exec already completed Popen's errpipe handshake. This stop does
     * not deadlock its constructor as a stopped Python preexec_fn would.
     */
    if (ptrace(PTRACE_TRACEME, 0, NULL, NULL) < 0 || raise(SIGSTOP)) return 125;
    execve(argv[2], argv + 2, environ);
    _exit(125);
}
