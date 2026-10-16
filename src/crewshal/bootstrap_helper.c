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
#include <linux/sched.h>
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
#include <sys/mount.h>
#include <sys/resource.h>
#include <sys/socket.h>
#include <sys/ptrace.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <sys/timerfd.h>
#include <sys/vfs.h>
#include <sys/statvfs.h>
#include <sys/sysmacros.h>
#include <linux/capability.h>
#include <grp.h>
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
#if defined(__x86_64__)
        DENY_SYSCALL(SYS_mknod),
#endif
        DENY_SYSCALL(SYS_keyctl), DENY_SYSCALL(SYS_add_key),
        DENY_SYSCALL(SYS_request_key),
        /* These newer paths must not bypass anonymous/asynchronous admission. */
        DENY_SYSCALL(447U), /* memfd_secret, both supported native ABIs */
        DENY_SYSCALL(425U), /* io_uring_setup */
        DENY_SYSCALL(463U), /* setxattrat */
        /* Shared anonymous mappings create sparse shmem inodes without file
         * growth checks. AppArmor separately denies every zero-device alias.
         * Ordinary shared file mappings, including SQLite WAL, remain valid.
         */
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_mmap, 0, 6),
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, args[3])),
        BPF_JUMP(BPF_JMP | BPF_JSET | BPF_K, MAP_ANONYMOUS, 0, 4),
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
    int original[15], retained[15];
    struct stat st;
    struct statfs fs;
    if (count < 1 || count > 15) return 125;
    for (int i = 0; i < count; ++i) {
        char *end;
        errno = 0;
        long value = strtol(numbers[i], &end, 10);
        if (errno || !numbers[i][0] || *end || value < 3 || value > INT_MAX)
            return 125;
        original[i] = (int)value;
        for (int j = 0; j < i; ++j) if (original[j] == original[i]) return 125;
        if (fstat(original[i], &st)) return 125;
        if (namespace_setup == 2 || namespace_setup == 3 || namespace_setup == 6) {
            int groups = namespace_setup == 6 ? 12 : namespace_setup == 3 ? 4 : 3;
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
            } else if ((namespace_setup == 5 || namespace_setup == 7 || namespace_setup == 8 || namespace_setup == 9) && i == 6) {
                int kind = 0;
                socklen_t length = sizeof kind;
                if (!S_ISSOCK(st.st_mode) || st.st_uid != 0 ||
                    getsockopt(original[i], SOL_SOCKET, SO_TYPE, &kind, &length) ||
                    length != sizeof kind || kind != SOCK_SEQPACKET) return 125;
            } else if ((namespace_setup == 7 || namespace_setup == 8 || namespace_setup == 9) && i == 8) {
                if (!S_ISDIR(st.st_mode) || st.st_uid != 0 ||
                    (st.st_mode & 0022) ||
                    (fcntl(original[i], F_GETFL) & O_ACCMODE) != O_RDONLY ||
                    fstatfs(original[i], &fs) || fs.f_type != 0x5A3C69F0) return 125;
            } else if ((namespace_setup == 7 || namespace_setup == 8 || namespace_setup == 9) && i == 9) {
                int seals = F_SEAL_WRITE | F_SEAL_GROW | F_SEAL_SHRINK | F_SEAL_SEAL;
                if (!S_ISREG(st.st_mode) || st.st_uid != 0 ||
                    st.st_size <= 0 || st.st_size > 2097152 ||
                    (fcntl(original[i], F_GETFL) & O_ACCMODE) != O_RDONLY ||
                    fcntl(original[i], F_GET_SEALS) != seals) return 125;
            } else if ((namespace_setup == 8 || namespace_setup == 9) && i == 10) {
                if (!S_ISREG(st.st_mode) ||
                    (fcntl(original[i], F_GETFL) & O_ACCMODE) != O_RDONLY ||
                    fstatfs(original[i], &fs) || fs.f_type != NSFS_MAGIC ||
                    ioctl(original[i], NS_GET_NSTYPE) != CLONE_NEWNET) return 125;
            } else if (namespace_setup == 9 && i == 11) {
                if (!S_ISREG(st.st_mode) || st.st_uid != 0 ||
                    (fcntl(original[i], F_GETFL) & O_ACCMODE) != O_RDONLY ||
                    fstatfs(original[i], &fs) || fs.f_type != 0x5A3C69F0) return 125;
            } else if (i == (namespace_setup == 7 || namespace_setup == 8 || namespace_setup == 9 ? 7 : namespace_setup == 5 ? 7 : namespace_setup == 4 ? 6 : 5)) {
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

static int batch_timer_lanes(void) {
    /* Three one-use lanes retain their original worker/supervisor/setup/
     * validator controls at 3..14. The original observer lifeline is 15,
     * readiness is 16, the sealed origin is 17, and the timer is 18.
     * Lane selection cannot create another deadline or aggregate allowance.
     */
    uint64_t origin = 0, now = monotonic_ns();
    int timer = -1, result = 125;
    if (signal(SIGPIPE, SIG_IGN) == SIG_ERR || !now ||
        pread(17, &origin, sizeof origin, 0) != (ssize_t)sizeof origin ||
        !origin || origin > now || origin > UINT64_MAX - 600000000000ULL ||
        now >= origin + 570000000000ULL) goto stop;
    timer = timerfd_create(CLOCK_MONOTONIC, TFD_CLOEXEC | TFD_NONBLOCK);
    if (timer != 18) goto stop;
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
    do { written = write(16, ready, (size_t)length); } while (written < 0 && errno == EINTR);
    if (written != length || close(16) || close(17)) goto stop;
    struct pollfd events[2] = {{timer, POLLIN, 0}, {15, POLLIN, 0}};
    int polled;
    do { polled = poll(events, 2, -1); } while (polled < 0 && errno == EINTR);
    if (polled > 0) result = 0;
stop:
    /* Stop every worker before any validator or trusted parent. Unknown
     * emptiness ends later effects. No second recovery grace is available.
     */
    for (int lane = 0; lane < 3; ++lane)
        if (!empty_group(3 + 4 * lane) && stop_group(3 + 4 * lane)) result = 125;
    for (int lane = 0; lane < 3; ++lane)
        if (!empty_group(6 + 4 * lane) && stop_group(6 + 4 * lane)) result = 125;
    for (int lane = 0; lane < 3; ++lane)
        if (!empty_group(3 + 4 * lane) || !empty_group(6 + 4 * lane)) {
            result = 125;
            goto finish;
        }
    for (int lane = 0; lane < 3; ++lane) {
        if (stop_group(4 + 4 * lane)) result = 125;
        if (stop_group(5 + 4 * lane)) result = 125;
    }
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

/* The direct validator child installs only its retained views. NEWPID selects
 * a distinct namespace for descendants; this child keeps its active namespace.
 * The independent parent reads both identities before the validator can run.
 * A failure exits without releasing any storage or renewing its watchdog.
 */
static int validator_view(char **numbers) {
    int sources[5], retained[5];
    struct stat st;
    struct statvfs fs;
    for (int i = 0; i < 5; ++i) {
        char *end;
        errno = 0;
        long value = strtol(numbers[i], &end, 10);
        if (errno || !numbers[i][0] || *end || value < 3 || value > INT_MAX)
            return 125;
        sources[i] = (int)value;
        for (int j = 0; j < i; ++j) if (sources[j] == sources[i]) return 125;
        if (fstat(sources[i], &st)) return 125;
        if (i == 3) {
            if (!S_ISCHR(st.st_mode) || major(st.st_rdev) != 1 ||
                minor(st.st_rdev) != 3) return 125;
        } else {
            if (!S_ISDIR(st.st_mode) || fstatvfs(sources[i], &fs)) return 125;
            if ((i == 0 || i == 4) && !(fs.f_flag & ST_RDONLY)) return 125;
            if (i == 2 && (fs.f_flag & ST_RDONLY)) return 125;
        }
    }
    for (int i = 0; i < 5; ++i) {
        retained[i] = fcntl(sources[i], F_DUPFD_CLOEXEC, 16);
        if (retained[i] < 0) return 125;
    }
    for (int i = 0; i < 5; ++i)
        if (dup2(retained[i], i + 3) != i + 3) return 125;
    if (syscall(SYS_close_range, 8U, ~0U, 0U) < 0) return 125;
    struct rlimit limit;
    if (getrlimit(RLIMIT_FSIZE, &limit) || limit.rlim_cur != 131072 ||
        limit.rlim_max != 131072 || geteuid() != 0 ||
        unshare(CLONE_NEWNS | CLONE_NEWNET | CLONE_NEWIPC | CLONE_NEWUTS | CLONE_NEWPID) ||
        mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL)) return 125;
    /* Chroot through the original FD, not a replaced pathname or overmounted
     * old root. The copied root must already contain every mount target.
     */
    if (fchdir(3) || chroot(".") || chdir("/") ||
        mount("proc", "/proc", "proc", MS_NOSUID | MS_NODEV | MS_NOEXEC, "hidepid=2") ||
        mount("tmpfs", "/dev", "tmpfs", MS_NOSUID | MS_NOEXEC,
              "size=4096,nr_inodes=8,mode=0755") ||
        mkdir("/dev/shm", 0755)) return 125;
    int target = open("/dev/null", O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0600);
    if (target < 0 || close(target)) return 125;
    if (mount("/proc/self/fd/6", "/dev/null", NULL, MS_BIND, NULL) ||
        mount("/proc/self/fd/7", "/dev/shm", NULL, MS_BIND, NULL) ||
        mount(NULL, "/dev/shm", NULL,
              MS_BIND | MS_REMOUNT | MS_RDONLY | MS_NOSUID | MS_NODEV | MS_NOEXEC, NULL) ||
        mount(NULL, "/dev", NULL, MS_REMOUNT | MS_RDONLY | MS_NOSUID | MS_NOEXEC, NULL) ||
        mount("/proc/self/fd/4", "/candidate/owned", NULL, MS_BIND, NULL) ||
        mount(NULL, "/candidate/owned", NULL,
              MS_BIND | MS_REMOUNT | MS_RDONLY | MS_NOSUID | MS_NODEV, NULL) ||
        mount("/proc/self/fd/5", "/scratch", NULL, MS_BIND, NULL) ||
        mount(NULL, "/scratch", NULL, MS_BIND | MS_REMOUNT | MS_NOSUID | MS_NODEV, NULL))
        return 125;
    /* Empty every capability set before exec. The parent separately checks the
     * actual status, descriptors, mounts, limits and namespaces at trace stop.
     */
    for (int cap = 0; cap <= CAP_LAST_CAP; ++cap)
        if (prctl(PR_CAPBSET_DROP, cap, 0, 0, 0)) return 125;
    if (setgroups(0, NULL) || setresgid(65531, 65531, 65531) ||
        setresuid(65531, 65531, 65531)) return 125;
    struct __user_cap_header_struct header = {_LINUX_CAPABILITY_VERSION_3, 0};
    struct __user_cap_data_struct capabilities[2] = {{0}, {0}};
    if (syscall(SYS_capset, &header, capabilities) ||
        prctl(PR_CAP_AMBIENT, PR_CAP_AMBIENT_CLEAR_ALL, 0, 0, 0) ||
        prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) ||
        syscall(SYS_close_range, 3U, ~0U, 0U) < 0) return 125;
    return 0;
}

static int payload_storage_role(int validator) {
    /* Select and read the exact loaded role before the initial trace stop.
     * The original unfiltered tracer independently checks actual binary policy
     * and this label before resume, then checks the inherited kernel filter.
     */
    const char *role = validator ? "crewshal-2d-validator-storage-v1" :
                                   "crewshal-2d-native-storage-v1";
    char command[128], expected[128], observed[128];
    int length = snprintf(command, sizeof command, "changeprofile %s", role);
    int descriptor = open("/proc/self/attr/apparmor/current", O_WRONLY | O_CLOEXEC);
    if (descriptor < 0) return 125;
    ssize_t written;
    do { written = write(descriptor, command, (size_t)length); } while (written < 0 && errno == EINTR);
    if (close(descriptor) || written != length) return 125;
    descriptor = open("/proc/self/attr/apparmor/current", O_RDONLY | O_CLOEXEC);
    if (descriptor < 0) return 125;
    ssize_t count;
    do { count = read(descriptor, observed, sizeof observed); } while (count < 0 && errno == EINTR);
    int closed = close(descriptor);
    length = snprintf(expected, sizeof expected, "%s (enforce)\n", role);
    if (closed || count != length || memcmp(observed, expected, (size_t)length)) return 125;
    return 0;
}

static int qualification_tree_actor(int ordinal) {
    if (setsid() < 0) return 125;
    int handles[2];
    char own_proc[64];
    int length = snprintf(own_proc, sizeof own_proc, "/proc/%ld", (long)getpid());
    if (length <= 0 || length >= (int)sizeof own_proc) return 125;
    handles[0] = open(own_proc, O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
    handles[1] = (int)syscall(SYS_pidfd_open, getpid(), 0U);
    if (handles[0] < 0 || handles[1] < 0) return 125;
    struct statfs source;
    if (fstatfs(handles[0], &source) || source.f_type != PROC_SUPER_MAGIC) return 125;
    char packet[] = "TREE 1\n";
    packet[5] = (char)('0' + ordinal);
    struct iovec data = {packet, sizeof packet - 1};
    union { struct cmsghdr align; char bytes[CMSG_SPACE(sizeof handles)]; } ancillary;
    memset(&ancillary, 0, sizeof ancillary);
    struct msghdr message = {0};
    message.msg_iov = &data;
    message.msg_iovlen = 1;
    message.msg_control = ancillary.bytes;
    message.msg_controllen = sizeof ancillary.bytes;
    struct cmsghdr *rights = CMSG_FIRSTHDR(&message);
    rights->cmsg_level = SOL_SOCKET;
    rights->cmsg_type = SCM_RIGHTS;
    rights->cmsg_len = CMSG_LEN(sizeof handles);
    memcpy(CMSG_DATA(rights), handles, sizeof handles);
    if (sendmsg(3, &message, MSG_NOSIGNAL) != (ssize_t)(sizeof packet - 1) ||
        close(handles[0]) || close(handles[1]) || raise(SIGSTOP)) return 125;
    char go[4];
    ssize_t count;
    do { count = recv(3, go, sizeof go, 0); } while (count < 0 && errno == EINTR);
    if (count != 3 || memcmp(go, "GO\n", 3)) return 125;
    char heartbeat = (char)('0' + ordinal);
    if (signal(SIGPIPE, SIG_IGN) == SIG_ERR) return 125;
    ssize_t first;
    do { first = write(4, &heartbeat, 1); } while (first < 0 && errno == EINTR);
    if (first != 1) return 125;
    char ready[] = "READY 0\n";
    ready[6] = heartbeat;
    do { first = send(3, ready, sizeof ready - 1, MSG_NOSIGNAL); }
    while (first < 0 && errno == EINTR);
    if (first != (ssize_t)(sizeof ready - 1) || close(3)) return 125;
    for (;;) {
        /* This cadence creates no deadline or grace. Only the original
         * worker cgroup.kill terminates retained qualification descendants.
         */
        ssize_t written = write(4, &heartbeat, 1);
        if (written < 0 && errno != EINTR && errno != EAGAIN && errno != EPIPE)
            return 125;
        if (poll(NULL, 0, 100) < 0 && errno != EINTR) return 125;
    }
}

static int qualification_tree(char **numbers) {
    int original[2], retained[2];
    struct stat st;
    for (int i = 0; i < 2; ++i) {
        char *end;
        errno = 0;
        long value = strtol(numbers[i], &end, 10);
        if (errno || !numbers[i][0] || *end || value < 3 || value > INT_MAX)
            return 125;
        original[i] = (int)value;
        if ((i && original[0] == original[1]) || fstat(original[i], &st)) return 125;
        if (!i) {
            int kind = 0;
            socklen_t length = sizeof kind;
            if (!S_ISSOCK(st.st_mode) ||
                getsockopt(original[i], SOL_SOCKET, SO_TYPE, &kind, &length) ||
                length != sizeof kind || kind != SOCK_SEQPACKET) return 125;
        } else if (!S_ISFIFO(st.st_mode) ||
                   (fcntl(original[i], F_GETFL) & (O_ACCMODE | O_NONBLOCK)) !=
                   (O_WRONLY | O_NONBLOCK)) return 125;
    }
    for (int i = 0; i < 2; ++i) {
        retained[i] = fcntl(original[i], F_DUPFD_CLOEXEC, 16);
        if (retained[i] < 0) return 125;
    }
    for (int i = 0; i < 2; ++i)
        if (dup2(retained[i], i + 3) != i + 3) return 125;
    gid_t groups[2];
    int group_count = getgroups(2, groups);
    struct __user_cap_header_struct header = {_LINUX_CAPABILITY_VERSION_3, 0};
    struct __user_cap_data_struct capabilities[2] = {{0}, {0}};
    if (syscall(SYS_close_range, 5U, ~0U, 0U) < 0 ||
        getuid() != 65534 || geteuid() != 65534 || getgid() != 65534 || getegid() != 65534 ||
        group_count < 0 || group_count > 1 || (group_count == 1 && groups[0] != 65534) ||
        syscall(SYS_capget, &header, capabilities) ||
        capabilities[0].effective || capabilities[0].permitted || capabilities[0].inheritable ||
        capabilities[1].effective || capabilities[1].permitted || capabilities[1].inheritable ||
        prctl(PR_GET_NO_NEW_PRIVS, 0, 0, 0, 0) != 1 ||
        payload_storage_role(0) || payload_storage_filter()) return 125;
    pid_t child = fork();
    if (child < 0) return 125;
    if (child) return 0;
    pid_t grandchild = fork();
    if (grandchild < 0) return 125;
    return qualification_tree_actor(grandchild ? 1 : 2);
}

static int network_tool_exec(int argc, char **argv) {
    if (argc < 4 || geteuid() != 0 || environ[0] != NULL ||
        (strcmp(argv[2], "0") && strcmp(argv[2], "4"))) return 125;
    const char *executable = !strcmp(argv[3], "ip") ? "/usr/sbin/ip" :
                             !strcmp(argv[3], "nft") ? "/usr/sbin/nft" : NULL;
    if (!executable) return 125;
    if (!strcmp(argv[2], "4")) {
        struct statfs source;
        if (fstatfs(4, &source) || source.f_type != NSFS_MAGIC ||
            ioctl(4, NS_GET_NSTYPE) != CLONE_NEWNET ||
            (fcntl(4, F_GETFL) & O_ACCMODE) != O_RDONLY) return 125;
    }
    struct stat st;
    struct statvfs fs;
    if (stat(executable, &st) || !S_ISREG(st.st_mode) || st.st_uid != 0 ||
        (st.st_mode & 0022) || !(st.st_mode & 0111) ||
        statvfs(executable, &fs) || !(fs.f_flag & ST_RDONLY) || chdir("/") ||
        syscall(SYS_close_range, !strcmp(argv[2], "4") ? 5U : 3U, ~0U, 0U) < 0 ||
        ptrace(PTRACE_TRACEME, 0, NULL, NULL) < 0 || raise(SIGSTOP)) return 125;
    argv[3] = (char *)executable;
    execve(executable, argv + 3, environ);
    return 125;
}

static int network_tool_root(int argc, char **argv) {
    if (argc < 7 || geteuid() != 0 || environ[0] != NULL || strcmp(argv[5], "--") ||
        (strcmp(argv[6], "ip") && strcmp(argv[6], "nft"))) return 125;
    int descriptors[3] = {-1, -1, -1}, keep_network = 0;
    for (int i = 0; i < 3; ++i) {
        char *end;
        errno = 0;
        long value = strtol(argv[i + 2], &end, 10);
        if (errno || !argv[i + 2][0] || *end || value > INT_MAX ||
            (i == 1 ? value != 0 && value < 3 : value < 3)) return 125;
        if (i == 1 && value == 0) continue;
        descriptors[i] = fcntl((int)value, F_DUPFD_CLOEXEC, 16);
        if (descriptors[i] < 0) return 125;
    }
    struct stat st;
    struct statvfs fs;
    if (fstat(descriptors[0], &st) || !S_ISDIR(st.st_mode) || st.st_uid != 0 ||
        (st.st_mode & 0022) ||
        (fcntl(descriptors[0], F_GETFL) & O_ACCMODE) != O_RDONLY ||
        fstatvfs(descriptors[0], &fs) || !(fs.f_flag & ST_RDONLY))
        return 125;
    if (descriptors[1] >= 0) {
        struct statfs source;
        if (fstatfs(descriptors[1], &source) || source.f_type != NSFS_MAGIC ||
            ioctl(descriptors[1], NS_GET_NSTYPE) != CLONE_NEWNET ||
            (fcntl(descriptors[1], F_GETFL) & O_ACCMODE) != O_RDONLY) return 125;
        keep_network = 1;
    }
    struct statfs source;
    if (fstatfs(descriptors[2], &source) || source.f_type != NSFS_MAGIC ||
        ioctl(descriptors[2], NS_GET_NSTYPE) != CLONE_NEWNS ||
        (fcntl(descriptors[2], F_GETFL) & O_ACCMODE) != O_RDONLY ||
        setns(descriptors[2], CLONE_NEWNS)) return 125;
    if (dup2(descriptors[0], 3) != 3 ||
        (keep_network && dup2(descriptors[1], 4) != 4) ||
        syscall(SYS_close_range, keep_network ? 5U : 4U, ~0U, 0U) < 0 ||
        unshare(CLONE_NEWNS) || mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL) ||
        mount("/proc/self", "/proc/self/fd/3/proc", NULL, MS_BIND, NULL) ||
        mount(NULL, "/proc/self/fd/3/proc", NULL,
              MS_BIND | MS_REMOUNT | MS_RDONLY | MS_NOSUID | MS_NODEV | MS_NOEXEC, NULL) ||
        fchdir(3) || chroot(".") || chdir("/") || close(3)) return 125;
    /* A fixed re-exec replaces host loader mappings before the first stop.
     * FD4 keeps only the original network target for a fixed ip netns argument.
     * The bounded creator controls the current network namespace separately.
     */
    argv[3] = "/bin/crewshal-bootstrap";
    argv[4] = "--network-tool-exec";
    argv[5] = keep_network ? "4" : "0";
    execve(argv[3], argv + 3, environ);
    return 125;
}

/* The original observer launches this static helper. The kernel places only
 * its child in the existing broker before the child's first instruction.
 * The launcher enters the same broker and waits for that exact child.
 * No external PID migration, new cgroup, or replacement timer occurs here.
 */
static int qualification_broker(char **numbers) {
    int sources[12], copies[12];
    struct stat st;
    struct statfs fs;
    struct statvfs volume;
    pid_t parent = getppid();
    if (parent <= 1 || prctl(PR_SET_PDEATHSIG, SIGKILL) || getppid() != parent ||
        prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)) return 125;
    for (int i = 0; i < 12; ++i) {
        char *end;
        errno = 0;
        long value = strtol(numbers[i], &end, 10);
        if (errno || !numbers[i][0] || *end || value < 3 || value > INT_MAX) return 125;
        sources[i] = (int)value;
        for (int j = 0; j < i; ++j) if (sources[j] == sources[i]) return 125;
        if (fstat(sources[i], &st)) return 125;
        if (i == 0) {
            if (!S_ISDIR(st.st_mode) || st.st_uid != 0 || (st.st_mode & 0022) ||
                fstatfs(sources[i], &fs) || fs.f_type != CGROUP2_SUPER_MAGIC) return 125;
        } else if (i == 1) {
            if (!S_ISDIR(st.st_mode) || st.st_uid != 0 || (st.st_mode & 0022) ||
                fstatvfs(sources[i], &volume) || !(volume.f_flag & ST_RDONLY)) return 125;
        } else if (i == 2) {
            int seals = F_SEAL_WRITE | F_SEAL_GROW | F_SEAL_SHRINK | F_SEAL_SEAL;
            if (!S_ISREG(st.st_mode) || st.st_size <= 0 || st.st_size > 65536 ||
                fcntl(sources[i], F_GET_SEALS) != seals) return 125;
        } else if (i == 3 || i == 4 || i == 8) {
            int kind = 0;
            socklen_t length = sizeof kind;
            if (!S_ISSOCK(st.st_mode) || getsockopt(sources[i], SOL_SOCKET, SO_TYPE, &kind, &length) ||
                kind != (i == 8 ? SOCK_SEQPACKET : SOCK_STREAM)) return 125;
        } else if (i == 11) {
            if (fstatfs(sources[i], &fs) || fs.f_type != NSFS_MAGIC ||
                ioctl(sources[i], NS_GET_NSTYPE) != CLONE_NEWNS) return 125;
        } else if (i == 9 || i == 10) {
            int expected = i == 9 ? O_RDONLY : (O_WRONLY | O_NONBLOCK);
            if (!S_ISFIFO(st.st_mode) ||
                (fcntl(sources[i], F_GETFL) & (O_ACCMODE | O_NONBLOCK)) != expected) return 125;
        } else if (!S_ISREG(st.st_mode) || st.st_uid != 0 || (st.st_mode & 0022) ||
                   (fcntl(sources[i], F_GETFL) & O_ACCMODE) != O_RDONLY ||
                   fstatvfs(sources[i], &volume) || !(volume.f_flag & ST_RDONLY)) return 125;
        copies[i] = fcntl(sources[i], F_DUPFD_CLOEXEC, 32);
        if (copies[i] < 0) return 125;
    }
    for (int i = 0; i < 12; ++i) if (dup2(copies[i], i + 3) != i + 3) return 125;
    if (syscall(SYS_close_range, 15U, ~0U, 0U) < 0) return 125;
    int placement = openat(3, "cgroup.procs", O_WRONLY | O_NOFOLLOW | O_CLOEXEC);
    char own[32];
    int length = snprintf(own, sizeof own, "%ld", (long)getpid());
    if (placement < 0 || write(placement, own, (size_t)length) != length || close(placement))
        return 125;
    struct clone_args creation = {0};
    creation.flags = CLONE_INTO_CGROUP;
    creation.exit_signal = SIGCHLD;
    creation.cgroup = 3;
    pid_t child = (pid_t)syscall(SYS_clone3, &creation, sizeof creation);
    if (child < 0) return 125;
    if (child == 0) {
        pid_t launcher = getppid();
        if (launcher <= 1 || prctl(PR_SET_PDEATHSIG, SIGKILL) || getppid() != launcher ||
            setns(14, CLONE_NEWNS) || unshare(CLONE_NEWNS) ||
            mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL) ||
            mount("proc", "/proc/self/fd/4/proc", "proc",
                  MS_RDONLY | MS_NOSUID | MS_NODEV | MS_NOEXEC, NULL) ||
            fchdir(4) || chroot(".") || chdir("/") || close(4) || close(14)) _exit(125);
        char *command[] = {"/bin/python3", "-I", "-S", "-B",
            "/opt/crewshal/lib/crewshal/linux_qualification_fixture.py", NULL};
        char *empty[] = {NULL};
        execve(command[0], command, empty);
        _exit(125);
    }
    /* Child controls must have no duplicate writer in the waiting launcher. */
    if (syscall(SYS_close_range, 3U, ~0U, 0U) < 0) return 125;
    int status = 0;
    pid_t waited;
    do { waited = waitpid(child, &status, 0); } while (waited < 0 && errno == EINTR);
    return waited == child && WIFEXITED(status) && WEXITSTATUS(status) == 0 ? 0 : 125;
}

/* Fixed stock device login is trusted preparation in the original live setup.
 * The outer observer retains this direct child before the login exec. */
static int authentication_prepare(char **numbers) {
    int sources[6], copies[6];
    struct stat st;
    struct statfs kind;
    struct statvfs fs;
    pid_t parent = getppid();
    if (geteuid() != 0 || environ[0] != NULL || parent <= 1 ||
        prctl(PR_SET_PDEATHSIG, SIGKILL) || getppid() != parent ||
        prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)) return 125;
    for (int i = 0; i < 6; ++i) {
        char *end;
        errno = 0;
        long value = strtol(numbers[i], &end, 10);
        if (errno || !numbers[i][0] || *end || value < 3 || value > INT_MAX) return 125;
        sources[i] = (int)value;
        for (int j = 0; j < i; ++j) if (sources[j] == sources[i]) return 125;
        if (fstat(sources[i], &st) ||
            (fcntl(sources[i], F_GETFL) & O_ACCMODE) != O_RDONLY) return 125;
        if (i == 0) {
            if (!S_ISDIR(st.st_mode) || fstatfs(sources[i], &kind) ||
                kind.f_type != CGROUP2_SUPER_MAGIC) return 125;
        } else if (i == 1) {
            if (!S_ISDIR(st.st_mode) || st.st_uid != 0 ||
                fstatvfs(sources[i], &fs) || !(fs.f_flag & ST_RDONLY)) return 125;
        } else if (i == 2) {
            if (!S_ISDIR(st.st_mode) || st.st_uid != 65534 || st.st_gid != 65534 ||
                (st.st_mode & 0077) || fstatvfs(sources[i], &fs) ||
                (fs.f_flag & ST_RDONLY)) return 125;
        } else if (i == 3 || i == 5) {
            int type = i == 3 ? CLONE_NEWNET : CLONE_NEWNS;
            if (fstatfs(sources[i], &kind) || kind.f_type != NSFS_MAGIC ||
                ioctl(sources[i], NS_GET_NSTYPE) != type) return 125;
        } else if (!S_ISCHR(st.st_mode) || st.st_rdev != makedev(1, 3)) return 125;
        copies[i] = fcntl(sources[i], F_DUPFD_CLOEXEC, 32);
        if (copies[i] < 0) return 125;
    }
    for (int i = 0; i < 6; ++i) if (dup2(copies[i], i + 3) != i + 3) return 125;
    if (syscall(SYS_close_range, 9U, ~0U, 0U) < 0) return 125;
    int control = openat(3, "cgroup.procs", O_WRONLY | O_NOFOLLOW | O_CLOEXEC);
    char own[32];
    int length = snprintf(own, sizeof own, "%ld", (long)getpid());
    if (control < 0 || write(control, own, (size_t)length) != length || close(control) ||
        setns(6, CLONE_NEWNET) || setns(8, CLONE_NEWNS) || unshare(CLONE_NEWNS) ||
        mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL) ||
        mount("proc", "/proc/self/fd/4/proc", "proc",
              MS_RDONLY | MS_NOSUID | MS_NODEV | MS_NOEXEC, "hidepid=2") ||
        mount("/proc/self/fd/5", "/proc/self/fd/4/native-auth", NULL, MS_BIND, NULL) ||
        mount(NULL, "/proc/self/fd/4/native-auth", NULL,
              MS_BIND | MS_REMOUNT | MS_NOSUID | MS_NODEV | MS_NOEXEC, NULL) ||
        mount("/proc/self/fd/7", "/proc/self/fd/4/dev/null", NULL, MS_BIND, NULL) ||
        fchdir(4) || chroot(".") || chdir("/")) return 125;
    for (int cap = 0; cap <= CAP_LAST_CAP; ++cap)
        if (prctl(PR_CAPBSET_DROP, cap, 0, 0, 0)) return 125;
    struct rlimit limit = {131072, 131072};
    if (setrlimit(RLIMIT_FSIZE, &limit) || setgroups(0, NULL) ||
        setresgid(65534, 65534, 65534) || setresuid(65534, 65534, 65534)) return 125;
    struct __user_cap_header_struct header = {_LINUX_CAPABILITY_VERSION_3, 0};
    struct __user_cap_data_struct caps[2] = {{0}, {0}};
    if (syscall(SYS_capset, &header, caps) ||
        prctl(PR_CAP_AMBIENT, PR_CAP_AMBIENT_CLEAR_ALL, 0, 0, 0) ||
        prctl(PR_SET_PDEATHSIG, SIGKILL) || getppid() != parent ||
        syscall(SYS_close_range, 3U, ~0U, 0U) < 0) return 125;
    char *helper[] = {"/bin/crewshal-bootstrap", "--authentication-exec", NULL};
    execve(helper[0], helper, environ);
    return 125;
}

static int authentication_exec(void) {
    struct __user_cap_header_struct header = {_LINUX_CAPABILITY_VERSION_3, 0};
    struct __user_cap_data_struct caps[2] = {{0}, {0}};
    if (geteuid() != 65534 || getegid() != 65534 || environ[0] != NULL ||
        syscall(SYS_capget, &header, caps) || caps[0].effective || caps[0].permitted ||
        caps[0].inheritable || caps[1].effective || caps[1].permitted || caps[1].inheritable ||
        prctl(PR_GET_NO_NEW_PRIVS, 0, 0, 0, 0) != 1 ||
        payload_storage_role(0) || payload_storage_filter() ||
        ptrace(PTRACE_TRACEME, 0, NULL, NULL) < 0 || raise(SIGSTOP)) return 125;
    char *command[] = {"/opt/codex/bin/codex", "--config",
                      "cli_auth_credentials_store=\"file\"", "login", "--device-auth", NULL};
    char *environment[] = {"HOME=/native-auth", "CODEX_HOME=/native-auth",
                           "PATH=/usr/bin:/bin", NULL};
    execve(command[0], command, environment);
    return 125;
}

int main(int argc, char **argv) {
    if (argc == 2 && strcmp(argv[1], "--authentication-exec") == 0)
        return authentication_exec();
    if (argc == 8 && strcmp(argv[1], "--authentication-preparation-fds") == 0)
        return authentication_prepare(argv + 2);
    if (argc == 14 && strcmp(argv[1], "--qualification-broker-fds") == 0)
        return qualification_broker(argv + 2);
    if (argc >= 7 && strcmp(argv[1], "--network-tool-root-fds") == 0)
        return network_tool_root(argc, argv);
    if (argc >= 4 && strcmp(argv[1], "--network-tool-exec") == 0)
        return network_tool_exec(argc, argv);
    if (argc == 4 && strcmp(argv[1], "--qualification-tree-fds") == 0)
        return qualification_tree(argv + 2);
    if (argc >= 9 && strcmp(argv[1], "--validator-view-fds") == 0) {
        pid_t original_parent = getppid();
        if (original_parent <= 1 || prctl(PR_SET_PDEATHSIG, SIGKILL) ||
            getppid() != original_parent) return 125;
        if (strcmp(argv[7], "--") || argv[8][0] != '/' || !argv[8][1] ||
            validator_view(argv + 2)) return 125;
        /* Credential changes clear PDEATHSIG. Restore it and check the same
         * original parent before the exact helper checkpoint re-exec.
         */
        if (prctl(PR_SET_PDEATHSIG, SIGKILL) || getppid() != original_parent)
            return 125;
        /* Re-exec supplies the existing exact validator helper argv. */
        argv[6] = "/bin/crewshal-bootstrap";
        argv[7] = "--validator";
        execve(argv[6], argv + 6, environ);
        return 125;
    }
    if (argc == 8 && strcmp(argv[1], "--batch-timer-fds") == 0) {
        if (control_fds(argv + 2, 6, 2)) return 125;
        return batch_timer(0);
    }
    if (argc == 9 && strcmp(argv[1], "--batch-timer-validator-fds") == 0) {
        if (control_fds(argv + 2, 7, 3)) return 125;
        return batch_timer(1);
    }
    if (argc == 17 && strcmp(argv[1], "--batch-timer-lanes-fds") == 0) {
        if (control_fds(argv + 2, 15, 6)) return 125;
        return batch_timer_lanes();
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
    if (argc >= 15 && strcmp(argv[1], "--namespace-validator-bridge-policy-source-fds") == 0) {
        if (strcmp(argv[12], "--") || strcmp(argv[13], "/usr/bin/bwrap") ||
            control_fds(argv + 2, 10, 7) || enter_setup_child()) return 125;
        /* Input storage namespace 10 is consumed here. Normalize original
         * policy namespace 11 and sealed policy 12 to parent FDs 10 and 11.
         * The parent separately checks the loaded export and exact profile
         * directories before it can resume any payload helper.
         */
        if (setns(10, CLONE_NEWNS) || close(10) ||
            dup2(11, 10) != 10 || dup2(12, 11) != 11 || close(12)) return 125;
        execve(argv[13], argv + 13, environ);
        return 125;
    }
    if (argc >= 16 && strcmp(argv[1], "--namespace-validator-bridge-policy-network-source-fds") == 0) {
        if (strcmp(argv[13], "--") || strcmp(argv[14], "/usr/bin/bwrap") ||
            control_fds(argv + 2, 11, 8) || enter_setup_child()) return 125;
        for (int i = 15; i < argc; ++i)
            if (!strcmp(argv[i], "--unshare-net") || !strcmp(argv[i], "--unshare-all"))
                return 125;
        /* Enter the original private network before exec. Stock bubblewrap
         * v0.11.0 has no --netns option; this argv must not unshare networking.
         * Keep network FD12 only for the original parent's later readback.
         */
        if (setns(10, CLONE_NEWNS) || close(10) || setns(13, CLONE_NEWNET) ||
            dup2(11, 10) != 10 || dup2(12, 11) != 11 ||
            dup2(13, 12) != 12 || close(13)) return 125;
        execve(argv[14], argv + 14, environ);
        return 125;
    }
    if (argc >= 17 && strcmp(argv[1], "--namespace-validator-bridge-policy-export-network-source-fds") == 0) {
        if (strcmp(argv[14], "--") || strcmp(argv[15], "/usr/bin/bwrap") ||
            control_fds(argv + 2, 12, 9) || enter_setup_child()) return 125;
        for (int i = 16; i < argc; ++i)
            if (!strcmp(argv[i], "--unshare-net") || !strcmp(argv[i], "--unshare-all"))
                return 125;
        /* Preserve the opened current policy export after the parent drops
         * privilege. The parent checks every current role target inode.
         */
        if (setns(10, CLONE_NEWNS) || close(10) || setns(13, CLONE_NEWNET) ||
            dup2(11, 10) != 10 || dup2(12, 11) != 11 ||
            dup2(13, 12) != 12 || dup2(14, 13) != 13 || close(14)) return 125;
        execve(argv[15], argv + 15, environ);
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
    if (payload_storage_role(validator) ||
        ptrace(PTRACE_TRACEME, 0, NULL, NULL) < 0 || raise(SIGSTOP)) return 125;
    if (payload_storage_filter()) return 125;
    execve(argv[2], argv + 2, environ);
    _exit(125);
}
