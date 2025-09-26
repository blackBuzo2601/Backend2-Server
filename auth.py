from database import check_user, user_exists, create_user

def login_user(username, password):
    return check_user(username, password)

def register_user(username, password):
    if user_exists(username):
        return False, "Ese nombre de usuario ya existe."
    create_user(username, password)
    return True, f"Usuario '{username}' registrado correctamente."
