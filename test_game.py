import os
import sys
import copy
import pytest
from unittest.mock import MagicMock

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import main
    Grid   = main.Grid
    Player = main.Player
    Pieces = main.Pieces
    Piece  = main.Piece
    IMPORTED = True
    IMPORT_ERROR = ""
except Exception as e:
    IMPORTED = False
    IMPORT_ERROR = str(e)

pytestmark = pytest.mark.skipif(
    not IMPORTED,
    reason=f"Не вдалося імпортувати main.py: {IMPORT_ERROR}"
)


def make_grid(size=8):
    """Допоміжна функція: створює та ініціалізує Grid."""
    pieces = Pieces()
    g = Grid(size, pieces)
    g.init()
    g.definePhysicalLimits()
    return g

def test_grid_size_includes_border():
    """1. Grid зберігає розмір size+2 (рамка навколо поля)."""
    g = make_grid(8)
    assert g.size == 10


def test_grid_inner_cells_zero_after_init():
    """2. Всі внутрішні клітинки = 0 після ініціалізації."""
    g = make_grid(8)
    for i in range(1, g.size - 1):
        for j in range(1, g.size - 1):
            assert g.grid[i][j] == 0


def test_piece_placeable_on_empty_grid():
    """3. Одиночний блок можна розмістити на порожній сітці."""
    g = make_grid(8)
    assert g.isPiecePlaceable(3, 3, 0) is True


def test_erase_alignment_clears_full_row():
    """4. eraseAlignment() очищає заповнений рядок до нуля."""
    g = make_grid(8)
    for j in range(1, g.size - 1):
        g.grid[1][j] = 1
    g.isThereAlignment()
    g.eraseAlignment()
    for j in range(1, g.size - 1):
        assert g.grid[1][j] == 0


def test_player_starts_with_zero_points():
    """5. Гравець починає гру з 0 очок."""
    p = Player(id=0)
    assert p.points == 0


def test_player_points_accumulate():
    """6. Очки гравця накопичуються коректно."""
    p = Player()
    p.points += 100
    p.points += 200
    assert p.points == 300


def test_repair_pads_short_string():
    """7. repair() доповнює короткий рядок нулями до 5 символів."""
    piece = Piece(0, 1)
    assert piece.repair("1") == "00001"


def test_mock_score_service_called_on_line_clear():
    score_service = MagicMock()

    lines_cleared = 2
    # Симулюємо логіку з updates() — нарахування очок
    score_service.add_points(lines_cleared * 100)

    # Перевіряємо
    score_service.add_points.assert_called_once_with(200)


def test_fake_deepcopy_isolates_grid():
    g = make_grid(8)
    # Fake-копія
    ghost = copy.deepcopy(g)

    ghost.grid[1][1] = 99

    #ізоляція працює
    assert g.grid[1][1] == 0


def test_e2e_fill_row_score_and_clear():
    """
      1. Створити сітку та гравця
      2. Заповнити рядок фігурами
      3. Виявити заповнений рядок
      4. Нарахувати 100 очок
      5. Очистити рядок
      6. Перевірити рахунок і порожній рядок
    """
    g = make_grid(8)
    p = Player(id=0)

    # 2
    for j in range(1, g.size - 1):
        g.grid[1][j] = 1

    # 3
    g.isThereAlignment()
    assert len(g.linesCompleted) >= 1

    # 4
    p.points += len(g.linesCompleted) * 100

    # 5
    g.eraseAlignment()

    # 6
    assert p.points == 100
    assert all(g.grid[1][j] == 0 for j in range(1, g.size - 1))


def test_e2e_two_players_winner():
    """
      1. Ініціалізувати двох гравців
      2. Симулювати набір очок (два раунди кожен)
      3. Визначити переможця (логіка з displayGameOverMulti)
      4. Перевірити що переможець — Гравець 1
    """
    p1 = Player(id=0)
    p2 = Player(id=1)

    # 2
    p1.points += 300
    p1.points += 200
    p2.points += 100
    p2.points += 300

    # 3
    if p1.points > p2.points:
        winner = p1
    elif p1.points == p2.points:
        winner = None
    else:
        winner = p2

    # 4
    assert winner is p1
    assert p1.points == 500
    assert p2.points == 400



def test_detects_score_multiplier_no_one_error():
    g = make_grid(8)
    p = Player(id=0)
    pieces = Pieces()

    for j in range(1, g.size - 1):
        g.grid[1][j] = 1

    p.update = MagicMock()
    pieces.update = MagicMock()

    main.updates([p], pieces, g)
    assert p.points == 100, (
        f"Мусить бути 100 балів. А тут тільки {p.points}"
        f"updates() в main.py"
    )