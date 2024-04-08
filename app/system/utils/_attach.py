class Attach:
    @staticmethod
    def attach_function(instance, function_name, function):
        setattr(instance, function_name, function)

    @staticmethod
    def attach_variable(instance, variable_name, value):
        setattr(instance, variable_name, value)

    @staticmethod
    def attach_thread(instance, thread_name, thread_instance):
        setattr(instance, thread_name, thread_instance)

    @staticmethod
    def attach_method(instance, method_name, method):
        setattr(instance, method_name, method)

    @staticmethod
    def attach_property(instance, prop_name, getter, setter=None):
        if setter:
            setattr(instance, prop_name, property(getter, setter))
        else:
            setattr(instance, prop_name, property(getter))

