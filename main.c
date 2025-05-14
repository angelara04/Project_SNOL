#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>

#define MAX 100
#define NAME_LEN 32

// Variable structure definition for SNOL
typedef enum { TYPE_INT, TYPE_FLOAT } VarType;

typedef struct {
    char name[NAME_LEN];
    VarType type;
    union {
        int i_val;
        float f_val;
    } value;
} Variable;

Variable variables[MAX];
int var_count = 0;

// Function Prototypes
int parse_command(char *input);
void handle_assignment_command(char *input);
void handle_beg_command(const char *var_name);
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

// Handler for assignment
void handle_assignment_command(char *input)
{
    printf("ASSIGNMENT detected: %s\n", input);
    // TODO: Parse and evaluate assignment expression
}

// Task #3 / Person #3 Subprograms
// Variable Management and Input Handling
// Helper: Check if variable name is valid
int is_valid_variable_name(const char *name) {
    if (!isalpha(name[0])) return 0;
    for (int i = 1; name[i] != '\0'; i++) {
        if (!isalnum(name[i])) return 0;
    }
    return 1;
}

// Helper: Check if input string is a valid int or float
int is_valid_number(const char *s) {
    int dot_count = 0;
    int start = (s[0] == '-') ? 1 : 0;
    int length = strlen(s);
    if (start == length) return 0;

    for (int i = start; s[i] != '\0'; i++) {
        if (s[i] == '.') {
            dot_count++;
            if (dot_count > 1) return 0;
        } else if (!isdigit(s[i])) {
            return 0;
        }
    }
    return 1;
}

// Search variable by name, return index or -1
int find_variable(const char *name) {
    for (int i = 0; i < var_count; i++) {
        if (strcmp(variables[i].name, name) == 0)
            return i;
    }
    return -1;
}

// BEG handler function
void handle_beg_command(const char *var_name) {
    if (!is_valid_variable_name(var_name)) {
        printf("SNOL> Error! Invalid variable name [%s]!\n", var_name);
        return;
    }

    char input[100];
    printf("SNOL> Please enter value for [%s]:\nInput: ", var_name);
    fgets(input, sizeof(input), stdin);
    input[strcspn(input, "\n")] = '\0'; // remove newline

    if (!is_valid_number(input)) {
        printf("SNOL> Error! Invalid number format for [%s]!\n", var_name);
        return;
    }

    int idx = find_variable(var_name);
    if (strchr(input, '.') != NULL) {
        float val = atof(input);
        if (idx != -1) {
            variables[idx].type = TYPE_FLOAT;
            variables[idx].value.f_val = val;
        } else {
            strncpy(variables[var_count].name, var_name, NAME_LEN);
            variables[var_count].type = TYPE_FLOAT;
            variables[var_count].value.f_val = val;
            var_count++;
        }
    } else {
        int val = atoi(input);
        if (idx != -1) {
            variables[idx].type = TYPE_INT;
            variables[idx].value.i_val = val;
        } else {
            strncpy(variables[var_count].name, var_name, NAME_LEN);
            variables[var_count].type = TYPE_INT;
            variables[var_count].value.i_val = val;
            var_count++;
        }
    }
}