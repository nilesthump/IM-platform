/* Test-only fixed-path helper; no product/SDK/API use. Device execution needs approval. */
#include <errno.h>
#include <stdio.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <sys/statvfs.h>
#include <unistd.h>

static const char source[] = "/data/local/tmp/im-gui-ca";
static const char target[] = "/apex/com.android.conscrypt/cacerts";

static int rollback(const char *stage, int failure) {
    fprintf(stderr, "%s errno=%d\n", stage, failure);
    if (umount(target) != 0) {
        fprintf(stderr, "ROLLBACK_FAILED errno=%d\n", errno);
        return 3;
    }
    fputs("OWNED_OVERLAY_REMOVED\n", stderr);
    return 2;
}

int main(int argc, char **argv) {
    struct stat source_info, target_info;
    struct statvfs view;
    (void)argv;
    if (argc != 1 || geteuid() != 0) {
        fputs("Root and no arguments required\n", stderr);
        return 1;
    }
    if (lstat(source, &source_info) != 0 || !S_ISDIR(source_info.st_mode) ||
        lstat(target, &target_info) != 0 || !S_ISDIR(target_info.st_mode)) {
        fputs("Fixed directory prerequisite failed\n", stderr);
        return 1;
    }
    if (mount(source, target, NULL, MS_BIND, NULL) != 0) {
        fprintf(stderr, "BIND_FAILED errno=%d\n", errno);
        return 1;
    }
    puts("BIND_CREATED");
    fflush(stdout);
    if (mount(NULL, target, NULL, MS_REMOUNT | MS_BIND | MS_RDONLY, NULL) != 0)
        return rollback("READONLY_REMOUNT_FAILED", errno);
    if (statvfs(target, &view) != 0)
        return rollback("READONLY_VIEW_CHECK_FAILED", errno);
    if ((view.f_flag & ST_RDONLY) == 0)
        return rollback("READONLY_VIEW_NOT_CONFIRMED", 0);
    puts("READONLY_VIEW_CONFIRMED; external topmost mount/CA checks still required");
    return 0;
}
