import click

from sabaa.setup import after_install as setup


def after_install():
	try:
		print("Setting up Sabaa HIS...")
		setup()

		click.secho("Thank you for installing Sabaa HIS!", fg="green")

	except Exception as e:
		pass
