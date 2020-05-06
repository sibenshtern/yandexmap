from typing import Union, Tuple

import requests


class API:
    MAP_API_SERVER = "http://static-maps.yandex.ru/1.x/"
    GEOCODER_API_SERVER = "http://geocode-maps.yandex.ru/1.x/"
    SEARCH_API_SERVER = "http://geocode-maps.yandex.ru/1.x/"

    GEOCODER_API_KEY = "40d1649f-0493-4b70-98ba-98533de7710b"
    SEARCH_API_KEY = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

    # consts for is ... else constructions
    COORDINATES_ARG = "coordinates"
    ADDRESS_ARG = "address"

    def __init__(
            self,
            coordinates: Union[None, Tuple[float, float]] = None,
            address: Union[None, str] = None
    ):
        self.points = []
        self.postal_code = None

        if coordinates is not None:
            self.coordinates = coordinates
            self.address = self.config_by_argument(
                self.COORDINATES_ARG
            )
        elif address is not None:
            self.address = address
            self.coordinates = self.config_by_argument(
                self.ADDRESS_ARG
            )
        else:
            raise Exception("All arguments are undefined")

    def config_by_argument(self, argument: str):
        if argument.startswith(self.COORDINATES_ARG):
            return self.get_address(self.coordinates)
        elif argument.startswith(self.ADDRESS_ARG):
            return self.get_coordinates(self.address)
        else:
            raise Exception(f'Unknown argument {argument}')

    def get_coordinates(
            self, geocode: Union[None, str] = None
    ) -> Tuple[float, ...]:
        toponym = self.get_toponym_by_geocoder(geocode)
        coordinates = toponym['Point']['pos']
        coordinates = tuple(map(float, coordinates.split()))
        return coordinates

    def get_address(self, coordinates: Tuple[float, ...]):
        str_coordinates = ','.join(map(str, coordinates))
        toponym = self.get_toponym_by_geocoder(str_coordinates)

        self.postal_code = toponym['metaDataProperty']['GeocoderMetaData'][
            'Address'].get('postal_code', None)
        address = toponym['metaDataProperty']['GeocoderMetaData']['text']
        return address

    def get_toponym_by_geocoder(self, geocode: str) -> dict:
        request_params = {
            "apikey": self.GEOCODER_API_KEY,
            "geocode": geocode,
            "format": "json"
        }

        response = requests.get(self.GEOCODER_API_SERVER, request_params)
        if not response:
            raise Exception(
                f'Response failed. Status code: {response.status_code}'
            )
        else:
            json_response = response.json()
            toponym = json_response['response']['GeoObjectCollection'][
                'featureMember'][0]['GeoObject']
            return toponym

    def return_coordinates(self) -> Tuple[float, ...]:
        return self.coordinates

    def return_address(self, postal_code: bool = False) -> str:
        if postal_code and self.postal_code is not None:
            return self.address + ', ' + self.postal_code
        return self.address

    def get_map(self, map_type, zoom):
        request_params = {
            'll': ','.join(map(str, self.coordinates)),
            'l': map_type,
            'z': zoom,
        }

        if len(self.points) > 0:
            request_params['pt'] = '~'.join(map(str, self.points))

        response = requests.get(self.MAP_API_SERVER, params=request_params)
        if not response:
            raise Exception(f'Request failed.')

        return response.content

    def add_point(self, point):
        self.points.append(point)

    def clear_points(self):
        self.points.clear()

    def set_coordinates(self, coordinates: Tuple[float, ...]) -> None:
        self.coordinates = coordinates
        self.config_by_argument(self.COORDINATES_ARG)

    def set_address(self, address: str) -> None:
        if self.validate_address(address):
            toponym = self.get_toponym_by_geocoder(address)
            toponym_address = toponym['metaDataProperty']['GeocoderMetaData'][
                'text']
            self.address = toponym_address
            self.postal_code = toponym['metaDataProperty'][
                'GeocoderMetaData']['Address'].get('postal_code', None)
        self.coordinates = self.config_by_argument(self.ADDRESS_ARG)

        self.clear_points()
        point_coordinates = self.return_coordinates()
        self.add_point(Point(point_coordinates))

    def validate_address(self, address) -> bool:
        try:
            self.get_toponym_by_geocoder(address)
            return True
        # catch Exception because self.get_toponym_by_geocoder raise
        # Exception when requests is bad
        except Exception as error:
            print(error)
            return False


class Point:

    def __init__(
            self, coordinates: Tuple[float, ...], marker_type: str = "comma"
    ):
        self.coordinates = coordinates
        self.marker_type = marker_type

    def __str__(self):
        return ",".join([*map(str, self.coordinates), self.marker_type])