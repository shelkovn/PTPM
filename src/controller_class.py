from user_inputs_getter import UserInterface, TkinterInterface
from repository import TriangleRepository, Triangle
from triangle_placer import triangle_placer
from external_service import ExternalServiceInterface


class GeometryController:
    def __init__(
        self, 
        view: TkinterInterface, 
        repository: TriangleRepository, 
        calculation_service: triangle_placer,
        external_service: ExternalServiceInterface
    ):
        self.view = view
        self.repository = repository
        self.calc_service = calculation_service
        self.external_service = external_service
        
        self.view.set_controller(self)

    def start_new_scenario(self) -> str:
        """Бизнес-логика сквозного сценария:
        1. Получение данных от пользователя.
        2. Поиск в БД (если есть - возврат из кэша, если нет - вычисление и сохранение).
        3. Отправка строки-результата сторонней зависимости.
        4. Отрисовка геометрии и возврат типа операции.
        """
        print("[Controller]: Starting.")
        
        raw_strings = self.view.get_user_data()
        if not raw_strings or len(raw_strings) < 3:
            msg = "inputs missing!"
            self.view.show_error(msg)
            return msg
            
        str_a, str_b, str_c = raw_strings
        
        try:
            a = float(str_a.replace(',', '.'))
            b = float(str_b.replace(',', '.'))
            c = float(str_c.replace(',', '.'))
        except ValueError:
            self.calc_service.calculate_triangle(str_a, str_b, str_c)
            self.view.show_error("Incorrect inputs!")
            return "Validation failed"

        print(f"[Controller]: searching ({a}, {b}, {c})...")
        db_triangle = self.repository.fetch_by_sides(a, b, c)

        if db_triangle:
            print(f"[Controller]: hit (ID: {db_triangle.id}).")
            triangle_type = db_triangle.triangle_type
            coords = [db_triangle.coord_a, db_triangle.coord_b, db_triangle.coord_c]
        else:
            print("[Controller]: miss. calculating:")
            triangle_type, coords = self.calc_service.calculate_triangle(str_a, str_b, str_c)
            
            error_msg = "Not a triangle" if triangle_type == "не треугольник" else None
            new_triangle = Triangle(
                side_a=a,
                side_b=b,
                side_c=c,
                coord_a=coords[0],
                coord_b=coords[1],
                coord_c=coords[2], 
                triangle_type=triangle_type,
                error_message=error_msg
            )
            try:
                self.repository.add_triangle(new_triangle)
                print(f"[Controller]: saved, ID: {new_triangle.id}")
            except Exception as e:
                print(f"[Controller]: database error: {e}")

        if triangle_type == "не треугольник" or coords == [(-1, -1)] * 3:
            self.view.show_error("not a triangle!")
            self.external_service.send_result("Error: invalid triangle")
            return "не треугольник"

        self.view.draw_triangle(coords, info_text=triangle_type)
        
        result_string = f"success. type: {triangle_type}"
        self.external_service.send_result(result_string)
        
        return triangle_type
