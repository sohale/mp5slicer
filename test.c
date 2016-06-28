#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

/* This is a slicer-wrapper compliant program. */

int main
(int ac, char **av)
{
    int     i;
    char    *buf = NULL;
    size_t  size;

    for (i=0;i<ac;i++) {
        fputs(av[i], stderr);
        fputc(10, stderr);
        sleep(1);
        if (!strcmp(av[i], "--crash"))
            exit(1);
        if (!strcmp(av[i], "--segv"))
            *buf = 0;
    }

    i = 0;
    while (getline(&buf, &size, stdin) != -1) {
        if (i) {
            fputs(buf, stdout);
            fputc(10, stdout);
            i = 0;
        }
        else
            i = 1;
    }
    return(0);
}
