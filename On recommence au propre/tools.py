def insert_line(router : str, index_line : int, data : str) -> None :
    """
    For a given router, insert the data at indexline in its config file
    """
    # Get the lines in the file and insert the new one
    with open(f"i{router[1::]}_startup_config.cfg", 'r') as file :
        lines = file.readlines()
        lines.insert(index_line, data)
    # Writes the updated list in the file
    with open(f"i{router[1::]}_startup_config.cfg", 'w') as file :
        file.writelines(lines)




def find_index(router : str, line : str) -> int :
    """ 
    For a given router, finds the index of a given line in its config file
    """
    current_index = 1
    with open(f'i{router[1:]}_startup-config.cfg', 'r') as file:
        # Browses the lines to find the wanted one
        lines = file.readline()
        while lines != line:
            lines = file.readline()
            current_index += 1
    return current_index