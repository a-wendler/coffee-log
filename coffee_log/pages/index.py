"""The home page of the app."""

from datetime import datetime
import reflex as rx
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from coffee_log import styles
from coffee_log.templates import template
from coffee_log.models.models import User, CoffeeLog, Payment


class CoffeeFormState(rx.State):
    """Das Eingabeformular der einzelnen Kaffee-Loggings."""

    anzahl = 1
    form_data: dict = {}
    success = 2

    def set_slider(self, anzahl: int):
        self.anzahl = anzahl

    def handle_submit(self, form_data: dict):
        self.form_data = form_data
        self.form_data["ts"] = datetime.now()

        try:
            with rx.session() as session:
                user = session.exec(
                    select(User).where(User.code == self.form_data["code"])
                ).scalar_one_or_none()

                log = CoffeeLog(
                    anzahl=self.form_data["anzahl"],
                    user=user,
                    ts=self.form_data["ts"],
                )
                session.add(log)
                session.commit()
            self.success = 1
        except IntegrityError:
            self.success = 0


@template(route="/", title="Home")
def index() -> rx.Component:
    """The home page.

    Returns:
        The UI for the home page.
    """

    return rx.vstack(
        rx.card(
            rx.form(
                rx.vstack(
                    rx.text("Wieviele Tassen Kaffee möchten Sie eintragen?"),
                    rx.hstack(
                        rx.text("1"),
                        rx.text("3"),
                        rx.text("5"),
                        width="100%",
                        justify="between",
                    ),
                    rx.slider(
                        name="anzahl",
                        default_value=1,
                        min=1,
                        max=5,
                        on_change=CoffeeFormState.set_slider,
                    ),
                    rx.spacer(),
                    rx.input(
                        name="code",
                        placeholder="Ihr Kennwort",
                        type="password",
                        required=True,
                    ),
                    rx.spacer(),
                    rx.button(
                        f"{CoffeeFormState.anzahl} Kaffee eintragen", type="submit"
                    ),
                ),
                on_submit=CoffeeFormState.handle_submit,
                reset_on_submit=True,
            ),
            size="3",
        ),
        rx.cond(
            CoffeeFormState.success == 1,
            rx.chakra.alert(
                rx.chakra.alert_icon(),
                rx.chakra.alert_title(
                    f"{CoffeeFormState.anzahl} Tassen Kaffee wurden registriert."
                ),
                status="success",
            ),
        ),
        rx.cond(
            CoffeeFormState.success == 0,
            rx.chakra.alert(
                rx.chakra.alert_icon(),
                rx.chakra.alert_title(
                    "Kennwort ungültig. Sie müssen sich erst registrieren."
                ),
                status="error",
            ),
        ),
        rx.text(CoffeeFormState.form_data.to_string()),
    )
