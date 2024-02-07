#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import os.path
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass


@dataclass(frozen=True)
class Route:
    start: str
    finish: str
    number: int


def add_route(routes: list[Route], start: str, finish: str, number: int) -> list[Route]:
    """
    Добавить данные о маршруте
    """

    routes.append(
        Route(
            start=start,
            finish=finish,
            number=number
        )
    )
    return routes


def display_route(routes: list[Route]) -> None:
    """
    Отобразить списко маршрутов
    """
    if routes:
        line = '+-{}-+-{}-+-{}-+-{}-+'.format(
            '-' * 4,
            '-' * 30,
            '-' * 20,
            '-' * 8
        )
        print(line)
        print(
            '| {:^4} | {:^30} | {:^20} | {:^8} |'.format(
                "№",
                "Начальный пункт",
                "Конечный пункт",
                "Номер маршрута"
            )
        )
        print(line)

        # Вывести данные о всех рейсах.
        for idx, route in enumerate(routes, 1):
            print(
                '| {:>4} | {:<30} | {:<20} | {:>8} |'.format(
                    idx,
                    route.start,
                    route.finish,
                    route.number
                )
            )
        print(line)
    else:
        print("Список маршрутов пуст.")


def select_route(routes: list[Route], period: int) -> list[Route]:
    """
    Выбрать маршрут
    """
    result = []
    for employee in routes:
        if employee.number == period:
            result.append(employee)

    return result


def save_routes(file_name: str, routes: list[Route]) -> None:
    """
    Сохранить всех работников в файл JSON.
    """
    root = ET.Element('routes')
    for route in routes:
        element = ET.Element('route')

        ET.SubElement(element, 'start', text=route.start)
        ET.SubElement(element, 'finish', text=route.finish)
        ET.SubElement(element, 'number', text=str(route.number))

        root.append(element)

    tree = ET.ElementTree(root)
    with open(file_name, "wb") as fout:
        tree.write(fout, encoding='utf8', xml_declaration=True)


def load_routes(file_name: str) -> list[Route]:
    """
    Загрузить всех работников из файла JSON.
    """
    with open(file_name, "r", encoding="utf-8") as fin:
        xml = fin.read()

        parser = ET.XMLParser(encoding="utf8")
        tree = ET.fromstring(xml, parser=parser)

        routes = []
        for element in tree.findall("route"):
            start = element.find("start").attrib.get("text")
            finish = element.find("finish").attrib.get("text")
            number = element.find("number").attrib.get("text")

            route = Route(start, finish, int(number))
            routes.append(route)

    return routes


def main(command_line=None):
    # Создать родительский парсер для определения имени файла.
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "-d",
        "--data",
        action="store",
        required=False,
        help="The data file name"
    )
    # Создать основной парсер командной строки.
    parser = argparse.ArgumentParser("routes")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    subparsers = parser.add_subparsers(dest="command")
    # Создать субпарсер для добавления маршрута.
    add = subparsers.add_parser(
        "add",
        parents=[file_parser],
        help="Add a new route"
    )
    add.add_argument(
        "-s",
        "--start",
        action="store",
        required=True,
        help="The start of the route"
    )
    add.add_argument(
        "-f",
        "--finish",
        action="store",
        help="The finish of the route"
    )
    add.add_argument(
        "-n",
        "--number",
        action="store",
        type=int,
        required=True,
        help="The number of the route"
    )
    # Создать субпарсер для отображения всех маршрутов.
    _ = subparsers.add_parser(
        "display",
        parents=[file_parser],
        help="Display all routes"
    )
    # Создать субпарсер для выбора маршрута.
    select = subparsers.add_parser(
        "select",
        parents=[file_parser],
        help="Select the route"
    )
    select.add_argument(
        "-N",
        "--numb",
        action="store",
        type=int,
        required=True,
        help="The route"
    )
    # Выполнить разбор аргументов командной строки.
    args = parser.parse_args(command_line)
    # Загрузить все маршруты из файла, если файл существует.
    data_file = args.data
    if not data_file:
        data_file = os.environ.get("WORKERS_DATA")
    if not data_file:
        print("The data file name is absent", file=sys.stderr)
        sys.exit(1)
    # Загрузить всех работников из файла, если файл существует.
    is_dirty = False
    if os.path.exists(data_file):
        routes = load_routes(data_file)
    else:
        routes = []
    # Добавить маршрут.
    if args.command == "add":
        routes = add_route(
            routes,
            args.start,
            args.finish,
            args.number
        )
        is_dirty = True
    # Отобразить все маршруты.
    elif args.command == "display":
        display_route(routes)
    # Выбрать требуемые маршруты.
    elif args.command == "select":
        selected = select_route(routes, args.numb)
        display_route(selected)
    # Сохранить данные в файл, если список маршрутов был изменен.
    if is_dirty:
        save_routes(data_file, routes)


if __name__ == '__main__':
    main()
