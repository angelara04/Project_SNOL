#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>

#define MAX 100

// Function Prototypes
int parse_command(char *input);
void handle_assignment_command(char *input);
void handle_beg_command(char *var);
void handle_print_command(char *var);
int is_assignment(char *input);
void print_error(const char *message);
void trim_whitespace(char *str);

// Main interpreter loop
int main()
{
    char input[MAX];

    printf("The SNOL environment is now active, you may proceed with giving your commands.\n");

    while (1)
    {
        printf("Command: ");
        if (fgets(input, MAX, stdin) == NULL)
            break;

        input[strcspn(input, "\n")] = '\0'; // Strip newline
        trim_whitespace(input);             // Remove leading/trailing spaces

        if (strlen(input) == 0)
            continue;

        int result = parse_command(input);

        if (result == -1)
        {
            printf("Exiting SNOL interpreter...\n");
            break;
        }
        else if (result == 0)
        {
            print_error("Invalid or unknown command");
        }
    }

    return 0;
}

// Strip leading and trailing whitespace
void trim_whitespace(char *str)
{
    // Trim leading spaces
    while (isspace(*str))
        str++;

    // Move trimmed string to beginning
    memmove(str, str, strlen(str) + 1);

    // Trim trailing spaces
    char *end = str + strlen(str) - 1;
    while (end > str && isspace(*end))
        *end-- = '\0';
}

// Error display
void print_error(const char *message)
{
    printf("SNOL ERROR: %s\n", message);
}

// Check if input has assignment
int is_assignment(char *input)
{
    return strchr(input, '=') != NULL;
}

// Command parser and dispatcher
int parse_command(char *input)
{
    // Copy input for safe editing
    char temp[MAX];
    strcpy(temp, input);

    // Check for assignment first
    if (is_assignment(temp))
    {
        handle_assignment_command(temp);
        return 1;
    }

    // Handle EXIT! exactly
    if (strcmp(temp, "EXIT!") == 0)
        return -1;

    // Check for PRINT and BEG with or without space
    if (strncmp(temp, "PRINT", 5) == 0)
    {
        char *arg = temp + 5;
        while (*arg == ' ')
            arg++; // Skip any spaces
        if (*arg == '\0')
        {
            print_error("Missing argument after PRINT");
            return 0;
        }
        handle_print_command(arg);
        return 1;
    }

    if (strncmp(temp, "BEG", 3) == 0)
    {
        char *arg = temp + 3;
        while (*arg == ' ')
            arg++;
        if (*arg == '\0')
        {
            print_error("Missing variable name after BEG");
            return 0;
        }
        handle_beg_command(arg);
        return 1;
    }

    return 0; // Unknown command
}

// Handler for PRINT
void handle_print_command(char *var)
{
    printf("PRINT called with variable/literal: %s\n", var);
    // TODO: Look up and print the value of var or literal
}

// Handler for BEG
void handle_beg_command(char *var)
{
    printf("BEG called with variable: %s\n", var);
    // TODO: Define variable and prompt user for value
}

// Handler for assignment
void handle_assignment_command(char *input)
{
    printf("ASSIGNMENT detected: %s\n", input);
    // TODO: Parse and evaluate assignment expression
}
