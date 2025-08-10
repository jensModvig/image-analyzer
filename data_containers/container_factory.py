from file_loaders import get_loader

def create_container(filepath):
    loader = get_loader(filepath)
    container_class = loader.container_type
    return container_class(filepath)