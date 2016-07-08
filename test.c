#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

/* This is a slicer-wrapper compliant program. */

typedef struct      s_list {

    char            *data;
    struct s_list   *next;
}                   t_list;

t_list *listnew
(char *content)
{
    t_list *new;

    if (new = malloc(sizeof(*new))) {
        new->data = strdup(content);
        new->next = NULL;
        return new;
    }
    else {
        return NULL;
    }
}

t_list *list_pushback
(t_list **list, t_list *new)
{
    t_list *current;

    if (*list) {
        current = *list;
        while (current->next) {
            current = current->next;
        }
        current->next = new;
    }
    else
        *list = new;
    return *list;
}

size_t list_len
(t_list *list)
{
    size_t len;

    len = 0;
    while (list) {
        list = list->next;
        len++;
    }
    return len;
}

int main
(int ac, char **av)
{
    int     i;
    char    *buf = NULL;
    size_t  size;
    size_t  len;
    t_list  *list;
    t_list  *old;

    for (i=0;i<ac;i++) {
        if (!strcmp(av[i], "--crash"))
            exit(1);
        if (!strcmp(av[i], "--segv"))
            *buf = 0;
    }

    list = NULL;
    while (getline(&buf, &size, stdin) != -1) {
        list_pushback(&list, listnew(buf));
    }

    len = list_len(list);
    i = 0;
    while (i < 100 && list)
    {
        if (i % 2) {
            fprintf(stdout, list->data);
//            fputc(10, stdout);
        }
        else {
            fprintf(stderr, "err: %s\n", list->data);
        }
        i++;
        old = list;
        list = list->next;
        free(old->data);
        free(old);
        fprintf(stderr, ">>>>%d\n", i * 100 / len);
        sleep(1);
    }
    return(0);
}
