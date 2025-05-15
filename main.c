#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>

#define MAX 100
#define MAX_VAR 100

// Enum to define variable types: INT_TYPE for integers and FLOAT_TYPE for floats
typedef enum { INT_TYPE, FLOAT_TYPE } VarType;

// Structure to represent a variable with its type and value
typedef struct {
    VarType type; // The type of the variable (int or float)
    union {
        int i_val; 
        float f_val; 
    } value; // Store either int or float value based on type
} Variable;

// Array to hold the names of the variables
char var_names[MAX_VAR][32];

// Array to hold the actual values of the variables
Variable var_values[MAX_VAR];

// Counter to keep track of the number of variables
int var_count = 0;


// Function Prototypes
int parse_command(char *input);
void handle_assignment_command(char *input);
void handle_beg_command(char *var);
void handle_print_command(char *var);
int is_assignment(char *input);
void print_error(const char *message);
void trim_whitespace(char *str);
int get_var_index(const char *name);
Variable parse_operand(const char *token);
Variable evaluate_expression(const char *left, const char *op, const char *right);

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
        handle_assignment_command(temp); // Handle assignment command
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
        handle_print_command(arg); // Handle PRINT command
        return 1;
    }

    if (strncmp(temp, "BEG", 3) == 0)
    {
        char *arg = temp + 3;
        while (*arg == ' ') 
            arg++; // Skip any spaces
        if (*arg == '\0')
        {
            print_error("Missing variable name after BEG");
            return 0;
        }
        handle_beg_command(arg); // Handle BEG command
        return 1;
    }

    return 0; // Unknown command
}

// Find variable index or -1
int get_var_index(const char *name)
{
    for (int i = 0; i < var_count; i++)
    {
        if (strcmp(var_names[i], name) == 0)
            return i;
    }
    return -1;
}

// Convert string/literal or variable to Variable type
Variable parse_operand(const char *token)
{
    Variable v;
    char *end;

    if (strchr(token, '.'))
    {
        v.type = FLOAT_TYPE;
        v.value.f_val = strtof(token, &end); // Convert string to float
        if (*end != '\0')
        {
            int idx = get_var_index(token); // Check if it's a variable
            if (idx == -1)
            {
                print_error("Undefined variable");
                exit(1);
            }
            v = var_values[idx]; // Use variable value
        }
    }
    else
    {
        v.type = INT_TYPE;
        v.value.i_val = strtol(token, &end, 10); // Convert string to integer
        if (*end != '\0')
        {
            int idx = get_var_index(token); // Check if it's a variable
            if (idx == -1)
            {
                print_error("Undefined variable");
                exit(1);
            }
            v = var_values[idx]; // Use variable value
        }
    }

    return v;
}

// Evaluate expression with two operands
Variable evaluate_expression(const char *left, const char *op, const char *right)
{
    Variable a = parse_operand(left);
    Variable b = parse_operand(right);

    if (a.type != b.type) // Ensure both operands are the same type
    {
        print_error("Incompatible types");
        exit(1);
    }

    Variable result;
    result.type = a.type;

    if (a.type == INT_TYPE)
    {
        int x = a.value.i_val;
        int y = b.value.i_val;

        if (strcmp(op, "+") == 0)
            result.value.i_val = x + y;
        else if (strcmp(op, "-") == 0)
            result.value.i_val = x - y;
        else if (strcmp(op, "*") == 0)
            result.value.i_val = x * y;
        else if (strcmp(op, "/") == 0)
            result.value.i_val = x / y;
        else if (strcmp(op, "%") == 0)
            result.value.i_val = x % y;
        else
        {
            print_error("Unknown operator");
            exit(1);
        }
    }
    else
    {
        float x = a.value.f_val;
        float y = b.value.f_val;

        if (strcmp(op, "+") == 0)
            result.value.f_val = x + y;
        else if (strcmp(op, "-") == 0)
            result.value.f_val = x - y;
        else if (strcmp(op, "*") == 0)
            result.value.f_val = x * y;
        else if (strcmp(op, "/") == 0)
            result.value.f_val = x / y;
        else
        {
            print_error("Invalid operator for float");
            exit(1);
        }
    }

    return result;
}

// Handler for assignment
void handle_assignment_command(char *input)
{
    printf("ASSIGNMENT detected: %s\n", input);

    // Parse assignment expression with left operand, operator, and right operand
    char var[32], left[32], op[4], right[32];
    if (sscanf(input, "%31s = %31s %3s %31s", var, left, op, right) == 4)
    {
        Variable val = evaluate_expression(left, op, right); // Evaluate the expression
        int idx = get_var_index(var); 
        if (idx == -1)
        {
            strcpy(var_names[var_count], var);
            var_values[var_count] = val;
            var_count++;
        }
        else
        {
            var_values[idx] = val; // Update existing variable
        }
    }
    else if (sscanf(input, "%31s = %31s", var, left) == 2)
    {
        Variable val = parse_operand(left); // Parse operand for simple assignment
        int idx = get_var_index(var);
        if (idx == -1)
        {
            strcpy(var_names[var_count], var);
            var_values[var_count] = val;
            var_count++;
        }
        else
        {
            var_values[idx] = val; // Update existing variable
        }
    }
    else
    {
        print_error("Invalid assignment format");
    }
}

// Handler for BEG
void handle_beg_command(char *var)
{
    printf("BEG called with variable: %s\n", var);

    // Prompt user for input
    char input[64];
    printf("Enter value for %s: ", var);
    if (fgets(input, sizeof(input), stdin) == NULL)
    {
        print_error("Input error");
        return;
    }

    input[strcspn(input, "\n")] = '\0'; // Remove newline character

    Variable val = parse_operand(input); // Parse input to determine variable type
    int idx = get_var_index(var);
    if (idx == -1)
    {
        strcpy(var_names[var_count], var);
        var_values[var_count] = val;
        var_count++;
    }
    else
    {
        var_values[idx] = val; // Update variable value
    }
}

// Handler for PRINT
void handle_print_command(char *var)
{
    printf("PRINT called with variable/literal: %s\n", var);

    // Check if it's a variable
    int idx = get_var_index(var);
    if (idx != -1)
    {
        if (var_values[idx].type == INT_TYPE)
            printf("SNOL> %s = %d\n", var, var_values[idx].value.i_val); // Print integer
        else
            printf("SNOL> %s = %.2f\n", var, var_values[idx].value.f_val); // Print float
    }
    else
    {
        // Handle literals
        char *end;
        if (strchr(var, '.')) // Check for float literal
        {
            float f = strtof(var, &end);
            if (*end == '\0')
            {
                printf("SNOL> %s = %.2f\n", var, f);
                return;
            }
        }
        else // Check for integer literal
        {
            int i = strtol(var, &end, 10);
            if (*end == '\0')
            {
                printf("SNOL> %s = %d\n", var, i);
                return;
            }
        }

        print_error("Unknown word or undefined variable");
    }
}
