class NotificationRouter:
    """
    Router to manage notification-related models in a separate database
    """
    notification_apps = {'notifications'}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.notification_apps:
            return 'notifications'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.notification_apps:
            return 'notifications'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.notification_apps:
            return db == 'notifications'
        return db == 'default'