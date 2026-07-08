from django.contrib.auth.password_validation import (
    UserAttributeSimilarityValidator as BaseSimilarityValidator,
    MinimumLengthValidator as BaseLengthValidator,
    CommonPasswordValidator as BaseCommonValidator,
    NumericPasswordValidator as BaseNumericValidator,
)


class UserAttributeSimilarityValidator(BaseSimilarityValidator):
    def get_help_text(self):
        return "Tu contraseña no puede ser similar a tu información personal."

    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except Exception:
            from django.core.exceptions import ValidationError
            raise ValidationError(
                "La contraseña es demasiado similar al nombre de usuario.",
                code="password_too_similar",
            )


class MinimumLengthValidator(BaseLengthValidator):
    def get_help_text(self):
        return f"Tu contraseña debe contener al menos {self.min_length} caracteres."

    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except Exception:
            from django.core.exceptions import ValidationError
            raise ValidationError(
                f"Esta contraseña es demasiado corta. Debe contener al menos {self.min_length} caracteres.",
                code="password_too_short",
            )


class CommonPasswordValidator(BaseCommonValidator):
    def get_help_text(self):
        return "Tu contraseña no puede ser una clave utilizada comúnmente."

    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except Exception:
            from django.core.exceptions import ValidationError
            raise ValidationError(
                "Esta contraseña es demasiado común.",
                code="password_too_common",
            )


class NumericPasswordValidator(BaseNumericValidator):
    def get_help_text(self):
        return "Tu contraseña no puede ser completamente numérica."

    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except Exception:
            from django.core.exceptions import ValidationError
            raise ValidationError(
                "Esta contraseña es completamente numérica.",
                code="password_entirely_numeric",
            )
