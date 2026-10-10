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
#include <linux/magic.h>
#include <linux/nsfs.h>
#include <linux/audit.h>
#include <linux/filter.h>
#include <linux/seccomp.h>
#include <stddef.h>
#include <poll.h>
#include <signal.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/prctl.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/ptrace.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/timerfd.h>
#include <sys/vfs.h>
#include <time.h>
#include <unistd.h>

extern char **environ;

/* Original anonymous-file/inode/key exclusion, inherited across exec and fork.
 * Trusted control capsules are created before this payload-only boundary.
 * The actual installed kernel program must be read by the unfiltered tracer;
 * a successful prctl, source hash or Seccomp status cannot establish it.
 */
#if defined(__x86_64__)
#define CREWSHAL_AUDIT_ARCH AUDIT_ARCH_X86_64
#elif defined(__aarch64__)
#define CREWSHAL_AUDIT_ARCH AUDIT_ARCH_AARCH64
#else
#error "Crewshal payload filter requires a qualified 64-bit Linux ABI"
#endif
#define DENY_SYSCALL(number) \
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, number, 0, 1), \
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | EPERM)
static int payload_storage_filter(void) {
    struct sock_filter instructions[] = {
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, arch)),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, CREWSHAL_AUDIT_ARCH, 1, 0),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, nr)),
        /* Reject x32/other high-number ABI aliases, even under x86_64 arch. */
        BPF_JUMP(BPF_JMP | BPF_JGE | BPF_K, 0x40000000U, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),
        DENY_SYSCALL(SYS_memfd_create), DENY_SYSCALL(SYS_shmget),
        DENY_SYSCALL(SYS_shmat), DENY_SYSCALL(SYS_linkat),
        DENY_SYSCALL(SYS_setxattr), DENY_SYSCALL(SYS_lsetxattr),
        DENY_SYSCALL(SYS_fsetxattr), DENY_SYSCALL(SYS_mknodat),
        DENY_SYSCALL(SYS_keyctl), DENY_SYSCALL(SYS_add_key),
        DENY_SYSCALL(SYS_request_key),
        /* These newer paths must not bypass anonymous/asynchronous admission. */
        DENY_SYSCALL(447U), /* memfd_secret, both supported native ABIs */
        DENY_SYSCALL(425U), /* io_uring_setup */
        DENY_SYSCALL(463U), /* setxattrat */
        /* Shared anonymous/dev-zero mappings create sparse shmem inodes
         * without the ordinary file-size growth checks. Do not infer their
         * logical bound from resident memory or available tmpfs blocks.
         */
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_mmap, 0, 5),
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, args[3])),
        BPF_STMT(BPF_ALU | BPF_AND | BPF_K, MAP_TYPE),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, MAP_SHARED, 1, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, MAP_SHARED_VALIDATE, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | EPERM),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
    };
    struct sock_fprog program = {
        .len = (unsigned short)(sizeof instructions / sizeof instructions[0]),
        .filter = instructions,
    };
    if (prctl(PR_GET_NO_NEW_PRIVS, 0, 0, 0, 0) != 1 ||
        prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &program)) return 125;
    return 0;
}

/* Normalize explicitly passed descriptors after Popen's exec handshake, never
 * from a Python preexec callback. Duplicate every input before replacing any
 * destination, so overlapping source/destination numbers cannot alias controls.
 * A failure refuses; the owning parent retains recovery responsibility.
 */
static int control_fds(char **numbers, int count, int namespace_setup) {
    int original[8], retained[8];
    struct stat st;
    struct statfs fs;
    if (count < 1 || count > 8) return 125;
    for (int i = 0; i < count; ++i) {
        char *end;
        errno = 0;
        long value = strtol(numbers[i], &end, 10);
        if (errno || !numbers[i][0] || *end || value < 3 || value > INT_MAX)
            return 125;
        original[i] = (int)value;
        for (int j = 0; j < i; ++j) if (original[j] == original[i]) return 125;
        if (fstat(original[i], &st)) return 125;
        if (namespace_setup == 2 || namespace_setup == 3) {
            int groups = namespace_setup == 3 ? 4 : 3;
            if (i < groups) {
                if (!S_ISDIR(st.st_mode) || st.st_uid != 0 ||
                    (st.st_mode & 0022) || fstatfs(original[i], &fs) ||
                    fs.f_type != CGROUP2_SUPER_MAGIC) return 125;
            } else if (i == groups + 2) {
                int seals = F_SEAL_WRITE | F_SEAL_GROW | F_SEAL_SHRINK | F_SEAL_SEAL;
                if (!S_ISREG(st.st_mode) || st.st_size != 8 ||
                    fcntl(original[i], F_GET_SEALS) != seals) return 125;
            } else {
                int mode = i == groups ? O_RDONLY : (O_WRONLY | O_NONBLOCK);
                if (!S_ISFIFO(st.st_mode) ||
                    (fcntl(original[i], F_GETFL) & (O_ACCMODE | O_NONBLOCK)) != mode)
                    return 125;
            }
        } else if (namespace_setup) {
            if (i == 0) {
                int seals = F_SEAL_WRITE | F_SEAL_GROW | F_SEAL_SHRINK | F_SEAL_SEAL;
                if (!S_ISREG(st.st_mode) || st.st_size <= 0 || st.st_size > 262144 ||
                    fcntl(original[i], F_GET_SEALS) != seals) return 125;
            } else if (namespace_setup == 5 && i == 6) {
                int kind = 0;
                socklen_t length = sizeof kind;
                if (!S_ISSOCK(st.st_mode) || st.st_uid != 0 ||
                    getsockopt(original[i], SOL_SOCKET, SO_TYPE, &kind, &length) ||
                    length != sizeof kind || kind != SOCK_SEQPACKET) return 125;
            } else if (i == (namespace_setup == 5 ? 7 : namespace_setup == 4 ? 6 : 5)) {
                if (!S_ISREG(st.st_mode) || fstatfs(original[i], &fs) ||
                    fs.f_type != NSFS_MAGIC ||
                    ioctl(original[i], NS_GET_NSTYPE) != CLONE_NEWNS) return 125;
            } else if (!S_ISDIR(st.st_mode) || st.st_uid != 0 ||
                       (st.st_mode & 0022) || fstatfs(original[i], &fs) ||
                       fs.f_type != CGROUP2_SUPER_MAGIC) return 125;
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

static int enter_setup_child(void) {
    /* Normalized FD 5 is the original checked setup directory. Only this
     * helper child migrates; its retaining observer stays outside every group
     * that terminal recovery may stop. No namespace/mount effect precedes it.
     */
    int control = openat(5, "cgroup.procs",
                         O_WRONLY | O_NONBLOCK | O_NOFOLLOW | O_CLOEXEC);
    if (control < 0) return 125;
    ssize_t written;
    do { written = write(control, "0", 1); } while (written < 0 && errno == EINTR);
    int closed = close(control);
    return written == 1 && closed == 0 ? 0 : 125;
}

static uint64_t monotonic_ns(void) {
    struct timespec value;
    if (clock_gettime(CLOCK_MONOTONIC, &value)) return 0;
    return (uint64_t)value.tv_sec * 1000000000ULL + (uint64_t)value.tv_nsec;
}

static int stop_group(int directory) {
    int descriptor = openat(directory, "cgroup.kill",
                            O_WRONLY | O_NONBLOCK | O_NOFOLLOW | O_CLOEXEC);
    if (descriptor < 0) return 125;
    ssize_t written;
    do { written = write(descriptor, "1", 1); } while (written < 0 && errno == EINTR);
    int closed = close(descriptor);
    return written == 1 && closed == 0 ? 0 : 125;
}

static int empty_group(int directory) {
    int descriptor = openat(directory, "cgroup.events", O_RDONLY | O_NONBLOCK | O_NOFOLLOW | O_CLOEXEC);
    if (descriptor < 0) return 0;
    char events[128];
    ssize_t count = read(descriptor, events, sizeof events - 1);
    int closed = close(descriptor);
    if (closed || count <= 0 || count >= (ssize_t)sizeof events - 1) return 0;
    events[count] = 0;
    if (strncmp(events, "populated 0\n", 12)) return 0;
    descriptor = openat(directory, "cgroup.procs", O_RDONLY | O_NONBLOCK | O_NOFOLLOW | O_CLOEXEC);
    if (descriptor < 0) return 0;
    char byte;
    count = read(descriptor, &byte, 1);
    closed = close(descriptor);
    return count == 0 && closed == 0;
}

static int batch_timer(int validator) {
    /* FDs: 3 worker, 4 supervisor, 5 setup, 6 original observer lifeline,
     * 7 readiness, 8 sealed original CLOCK_MONOTONIC origin, 9 timerfd.
     * With validator: 6 validator, 7 lifeline, 8 readiness, 9 origin, 10 timer.
     * No observer/aggregate kill interface is inherited. Production children
     * must enter setup before creation and remain covered by the original pool.
     * A terminal unknown never closes storage or grants release/reuse.
     */
    uint64_t origin = 0, now = monotonic_ns();
    int lifeline = validator ? 7 : 6, readiness = validator ? 8 : 7;
    int origin_fd = validator ? 9 : 8, timer_fd = validator ? 10 : 9;
    int timer = -1, result = 125;
    if (signal(SIGPIPE, SIG_IGN) == SIG_ERR || !now ||
        pread(origin_fd, &origin, sizeof origin, 0) != (ssize_t)sizeof origin ||
        !origin || origin > now || origin > UINT64_MAX - 600000000000ULL ||
        now >= origin + 570000000000ULL) goto stop;
    timer = timerfd_create(CLOCK_MONOTONIC, TFD_CLOEXEC | TFD_NONBLOCK);
    if (timer != timer_fd) goto stop;
    struct itimerspec limit = {0};
    limit.it_value.tv_sec = (time_t)((origin + 570000000000ULL) / 1000000000ULL);
    limit.it_value.tv_nsec = (long)((origin + 570000000000ULL) % 1000000000ULL);
    if (timerfd_settime(timer, TFD_TIMER_ABSTIME, &limit, NULL)) goto stop;
    char ready[128];
    int length = snprintf(ready, sizeof ready, "BATCH %llu %llu %llu\n",
                          (unsigned long long)origin,
                          (unsigned long long)(origin + 570000000000ULL),
                          (unsigned long long)(origin + 600000000000ULL));
    ssize_t written;
    do { written = write(readiness, ready, (size_t)length); } while (written < 0 && errno == EINTR);
    if (written != length || close(readiness) || close(origin_fd)) goto stop;
    struct pollfd events[2] = {{timer, POLLIN, 0}, {lifeline, POLLIN, 0}};
    int polled;
    do { polled = poll(events, 2, -1); } while (polled < 0 && errno == EINTR);
    if (polled > 0) result = 0;
stop:
    /* A hard batch cutoff supplies no second worker recovery grace. The native
     * lifetime owns its original one-second grace. Avoid another worker stop
     * when it is already empty; after a cutoff signal, unknown emptiness stops
     * all later effects instead of starting a new wait or recovery deadline.
     * No operational startup is permitted at/after the fixed reserve boundary.
     */
    if (!empty_group(3)) {
        if (stop_group(3)) result = 125;
    }
    if (validator && !empty_group(6) && stop_group(6)) result = 125;
    if (!empty_group(3) || (validator && !empty_group(6))) { result = 125; goto finish; }
    if (stop_group(4)) result = 125;
    if (stop_group(5)) result = 125;
finish:
    if (timer >= 0) close(timer);
    return result;
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
    if (argc == 8 && strcmp(argv[1], "--batch-timer-fds") == 0) {
        if (control_fds(argv + 2, 6, 2)) return 125;
        return batch_timer(0);
    }
    if (argc == 9 && strcmp(argv[1], "--batch-timer-validator-fds") == 0) {
        if (control_fds(argv + 2, 7, 3)) return 125;
        return batch_timer(1);
    }
    if (argc == 5 && strcmp(argv[1], "--watchdog-fds") == 0) {
        if (control_fds(argv + 2, 3, 0)) return 125;
        /* Re-exec establishes the existing exact armed argv checkpoint. */
        char *command[] = {"/bin/crewshal-bootstrap", "--watchdog", NULL};
        execve(command[0], command, environ);
        return 125;
    }
    if (argc >= 10 && strcmp(argv[1], "--namespace-fds") == 0) {
        if (strcmp(argv[7], "--") || strcmp(argv[8], "/usr/bin/bwrap") ||
            control_fds(argv + 2, 5, 1) || enter_setup_child()) return 125;
        execve(argv[8], argv + 8, environ);
        return 125;
    }
    if (argc >= 11 && strcmp(argv[1], "--namespace-source-fds") == 0) {
        if (strcmp(argv[8], "--") || strcmp(argv[9], "/usr/bin/bwrap") ||
            control_fds(argv + 2, 6, 1) || enter_setup_child()) return 125;
        /* Enter only the original retained storage namespace. Do not forward
         * its handle to the setup parent, native process or code tools.
         */
        if (setns(8, CLONE_NEWNS) || close(8)) return 125;
        execve(argv[9], argv + 9, environ);
        return 125;
    }
    if (argc >= 12 && strcmp(argv[1], "--namespace-validator-source-fds") == 0) {
        if (strcmp(argv[9], "--") || strcmp(argv[10], "/usr/bin/bwrap") ||
            control_fds(argv + 2, 7, 4) || enter_setup_child()) return 125;
        /* FD 8 is the original independent validator cgroup; only FD 9
         * is the original storage namespace. Preserve the former for parent
         * supervision and close the latter before the readonly-root exec.
         */
        if (setns(9, CLONE_NEWNS) || close(9)) return 125;
        execve(argv[10], argv + 10, environ);
        return 125;
    }
    if (argc >= 13 && strcmp(argv[1], "--namespace-validator-bridge-source-fds") == 0) {
        if (strcmp(argv[10], "--") || strcmp(argv[11], "/usr/bin/bwrap") ||
            control_fds(argv + 2, 8, 5) || enter_setup_child()) return 125;
        /* Original validator control 8 and custody socket 9 reach only the
         * trusted parent. Original storage namespace 10 is consumed here.
         */
        if (setns(10, CLONE_NEWNS) || close(10)) return 125;
        execve(argv[11], argv + 11, environ);
        return 125;
    }
    if (argc == 2 && strcmp(argv[1], "--watchdog") == 0) return watchdog();
    int validator = argc >= 3 && strcmp(argv[1], "--validator") == 0;
    if (!validator && (argc < 4 || strcmp(argv[1], "--exec") != 0 ||
        strcmp(argv[2], "/opt/codex/bin/codex") != 0)) return 125;
    if (validator && (argv[2][0] != '/' || !argv[2][1])) return 125;
    pid_t parent = getppid();
    if (parent <= 1 || prctl(PR_SET_PDEATHSIG, SIGKILL) || getppid() != parent) return 125;
    /* Preserve the route's exact cwd across exec; app-server's single fixed
     * task uses the candidate root. Admission independently verifies this.
     */
    const char *cwd = validator || strcmp(argv[3], "app-server") == 0 ?
                      "/candidate/owned" : "/scratch/checkout";
    if (chdir(cwd) || syscall(SYS_close_range, 3U, ~0U, 0U) < 0) return 125;
    /* Helper exec already completed Popen's errpipe handshake. This stop does
     * not deadlock its constructor as a stopped Python preexec_fn would.
     */
    if (ptrace(PTRACE_TRACEME, 0, NULL, NULL) < 0 || raise(SIGSTOP)) return 125;
    if (payload_storage_filter()) return 125;
    execve(argv[2], argv + 2, environ);
    _exit(125);
}
