import random
import string


def random_string_generator(size=10, chars=string.ascii_letters + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


def unique_code_generator(instance):
    new_code = random_string_generator(size=8)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(code=new_code).exists()
    if qs_exists:
        return unique_code_generator(instance)
    return new_code


def unique_password_generator(instance):
    new_password = random_string_generator(size=8)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(password=new_password).exists()
    if qs_exists:
        return unique_code_generator(instance)
    return new_password
