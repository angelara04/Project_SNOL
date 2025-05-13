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