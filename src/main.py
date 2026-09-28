import logging
from user_inputs_getter import UserInterface, TkinterInterface
from repository import TriangleRepository
from triangle_placer import triangle_placer
from external_service import ExternalService
from controller_class import GeometryController

def main():
    logger = logging.getLogger("TriangleApp")
    logger.info("Инициализация...")

    repository = TriangleRepository(db_path=":memory:") 
    
    view = TkinterInterface()
    calculation_service = triangle_placer()
    external_service = ExternalService()

    controller = GeometryController(
        view=view,
        repository=repository,
        calculation_service=calculation_service,
        external_service=external_service
    )

    logger.info("Приложение готово к работе. Запуск интерфейса...")

    view.run_ui()

if __name__ == "__main__":
    main()
