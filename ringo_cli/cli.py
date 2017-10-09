# -*- coding: utf-8 -*-

import click
import requests
import voorhees

SERVICES = {
        "users": {"url": "http://0.0.0.0:5000"}
}


@click.group()
@click.pass_context
def main(ctx):
    """CLI for the Ringo2 core service."""
    ctx.obj = {}
    pass


@click.group()
@click.argument('service', type=click.Choice(SERVICES))
@click.pass_context
def crud(ctx, service):
    """Send basic CRUD commands to a service."""
    ctx.obj["service"] = service


@click.group()
@click.pass_context
def admin(ctx):
    """Various administration commands."""
    pass


@click.command()
@click.argument('jsonfile', type=click.File('rb'))
@click.pass_context
def create(ctx, jsonfile):
    """Creates new item(s).

    The new item(s) are initialised with the values defined in the JSON
    file. Create is called for every dataset within the JSON file.
    """
    data = voorhees.from_json(jsonfile.read())
    if not isinstance(data, list):
        data = [data]

    total = len(data)
    service = ctx.obj["service"]
    for num, item in enumerate(data):
        click.echo('Creating ({}/{}) -> '.format(num+1, total), nl=False)
        response = requests.post("{}/{}".format(SERVICES[service]["url"], service), data=voorhees.to_json(item))
        color = "red" if (response.status_code >= 300) else "green"
        click.echo(click.style('{}'.format(response.status_code), fg=color))


@click.command()
@click.argument('id', type=click.INT)
@click.pass_context
def read(ctx, id):
    """Loads a single item."""
    service = ctx.obj["service"]
    response = requests.get("{}/{}/{}".format(SERVICES[service]["url"], service, id))
    if (response.status_code >= 300):
        color = "red"
        click.echo('Reading ID:{} -> '.format(id), nl=False)
        click.echo(click.style('{}'.format(response.status_code), fg=color))
    else:
        print(voorhees.prettify(response.text))


@click.command()
@click.argument('jsonfile', type=click.File('rb'))
@click.pass_context
def update(ctx, jsonfile):
    """Updates item(s).

    The item(s) are updated with the values defined in the JSON
    file. Update is called for every dataset within the JSON file.
    """
    data = voorhees.from_json(jsonfile.read())
    if not isinstance(data, list):
        data = [data]

    total = len(data)
    service = ctx.obj["service"]
    for num, item in enumerate(data):
        click.echo('Updating ID:{} ({}/{}) -> '.format(item["id"], num+1, total), nl=False)
        response = requests.put("{}/{}/{}".format(SERVICES[service]["url"], service, item["id"]),
                                data=voorhees.to_json(item))
        color = "red" if (response.status_code >= 300) else "green"
        click.echo(click.style('{}'.format(response.status_code), fg=color))


@click.command()
@click.argument('id', type=click.INT)
@click.pass_context
def delete(ctx, id):
    """Deletes a single item."""
    click.echo('Deleting ID:{} -> '.format(id), nl=False)
    service = ctx.obj["service"]
    response = requests.delete("{}/{}/{}".format(SERVICES[service]["url"], service, id))
    color = "red" if (response.status_code >= 300) else "green"
    click.echo(click.style('{}'.format(response.status_code), fg=color))


@click.command()
@click.pass_context
@click.option('--limit', help="Limit number of result", default=100)
@click.option('--offset', help="Return entries with an offset", default=0)
@click.option('--search', help="Define a search filter")
def search(ctx, limit, offset, search):
    """Search and list items."""
    service = ctx.obj["service"]
    params = {"limit": limit, "offset": offset, "search": search}
    response = requests.get("{}/{}".format(SERVICES[service]["url"], service), params=params)
    if (response.status_code >= 300):
        color = "red"
        click.echo('Searching -> ', nl=False)
        click.echo(click.style('{} ({})'.format(response.status_code, response.text), fg=color))
    else:
        print(voorhees.prettify(response.text))

########################################################################
#                            Admin commands                            #
########################################################################


@click.command()
@click.argument('id')
@click.option('--password', help="Password to be set")
@click.pass_context
def passwd(ctx, id, password):
    """Set/Reset user password.

    The password will be autogenerated on default. You can optionally
    provide a password by using the --password option."""
    service = "users"
    values = voorhees.to_json({"password": password})
    response = requests.post("{}/{}/{}/{}".format(SERVICES[service]["url"], service, id, "password"), data=values)
    if (response.status_code >= 300):
        color = "red"
        click.echo('Password reset -> ', nl=False)
        click.echo(click.style('{}'.format(response.status_code), fg=color))
    else:
        click.echo("{}".format(response.text))


main.add_command(crud)
main.add_command(admin)

crud.add_command(search)
crud.add_command(create)
crud.add_command(read)
crud.add_command(update)
crud.add_command(delete)

admin.add_command(passwd)


if __name__ == "__main__":
    main()
