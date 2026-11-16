"""
python -m unittest discover -s tests -t
"""

import logging
import os
import shutil
import sqlite3
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, call, patch

from curl_cffi.requests import RequestsError

from src.comment import Comment
from src.controller import ForumParserContoller
from src.logger import logger as app_logger
from src.mapper import save_to_db
from src.parser import parse_page
from src.repository import DatabaseRepository, DBRInterface
from src.scraper import HTMLScraperOutput, scrape_page

FIXTURE = Path(__file__).parent / "index.html"
URL = "https://gamefaqs.gamespot.com/boards/920607-devil-may-cry-3-dantes-awakening/80234849"

app_logger.setLevel(logging.ERROR)


def make_board(messages):
    """Build a minimal GameFAQs-like page.

    messages: iterable of (id, username, text, signature_or_None)
    """
    cells = []
    for msg_id, name, text, sig in messages:
        sig_html = f'<div class="signature">{sig}</div>' if sig else ""
        cells.append(
            f'<td class="msg" id="message_{msg_id}">'
            f'<a class="name" href="/user/{name}">{name}</a>'
            f'<div class="msg_text">{text}</div>'
            f"{sig_html}</td>"
        )
    return "<html><body><table><tr>" + "".join(cells) + "</tr></table></body></html>"

class RepositoryAddTests(unittest.TestCase):
    def setUp(self):
        self.repo = DatabaseRepository(":memory:")
        self.addCleanup(self.repo._conn.close)

    def test_add_returns_true_and_persists_comment(self):
        self.assertTrue(self.repo.add(1, "alice", "hello world"))
        self.assertEqual(
            self.repo.get_by_id(1), Comment(name="alice", message="hello world", id=1)
        )

    def test_add_strips_whitespace_from_name_and_message(self):
        self.repo.add(2, "  bob  ", "   hi there   ")
        stored = self.repo.get_by_id(2)
        self.assertEqual(stored.name, "bob")
        self.assertEqual(stored.message, "hi there")

    def test_add_rejects_non_int_id(self):
        for bad in ("abc", "1.5", None, [], {}):
            with self.subTest(comment_id=bad):
                with self.assertRaises(Exception) as ctx:
                    self.repo.add(bad, "alice", "hi")
                self.assertEqual(str(ctx.exception), "Not an int ID")

    def test_add_rejects_negative_id(self):
        with self.assertRaises(Exception) as ctx:
            self.repo.add(-1, "alice", "hi")
        self.assertEqual(str(ctx.exception), "Negative ID")
        self.assertIsNone(self.repo.get_by_id(-1))

    def test_add_rejects_empty_username(self):
        for bad in (None, "", "   \t "):
            with self.subTest(username=bad):
                with self.assertRaises(Exception) as ctx:
                    self.repo.add(1, bad, "hi")
                self.assertEqual(str(ctx.exception), "Empty username")

    def test_add_rejects_empty_message(self):
        for bad in (None, "", "   \n "):
            with self.subTest(message=bad):
                with self.assertRaises(Exception) as ctx:
                    self.repo.add(1, "alice", bad)
                self.assertEqual(str(ctx.exception), "Empty message")

    def test_add_duplicate_id_raises_integrity_error(self):
        self.repo.add(1, "alice", "first")
        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.add(1, "bob", "second")
        self.assertEqual(self.repo.get_by_id(1).name, "alice")  # row untouched

class RepositoryGetByIdTests(unittest.TestCase):
    def setUp(self):
        self.repo = DatabaseRepository(":memory:")
        self.addCleanup(self.repo._conn.close)
        self.repo.add(1, "alice", "hello")
        self.repo.add(2, "bob", "goodbye")

    def test_returns_comment_when_id_exists(self):
        self.assertEqual(
            self.repo.get_by_id(1), Comment(name="alice", message="hello", id=1)
        )

    def test_returns_none_when_id_is_missing(self):
        self.assertIsNone(self.repo.get_by_id(999))

    def test_accepts_numeric_string_id(self):
        self.assertEqual(self.repo.get_by_id("2").name, "bob")

    def test_raises_on_non_int_id(self):
        for bad in ("abc", None, []):
            with self.subTest(comment_id=bad):
                with self.assertRaises(Exception) as ctx:
                    self.repo.get_by_id(bad)
                self.assertEqual(str(ctx.exception), "Not an int ID")

class RepositoryGetByNameTests(unittest.TestCase):

    def setUp(self):
        self.repo = DatabaseRepository(":memory:")
        self.addCleanup(self.repo._conn.close)
        self.repo.add(1, "alice", "hello")
        self.repo.add(2, "bob", "goodbye")

    def test_returns_comment_for_existing_user(self):
        self.assertEqual(
            self.repo.get_by_name("alice"), Comment(name="alice", message="hello", id=1)
        )

    def test_returns_none_for_unknown_user(self):
        self.assertIsNone(self.repo.get_by_name("nobody"))

    def test_returns_first_comment_when_user_has_several(self):
        self.repo.add(10, "alice", "second post")
        self.assertEqual(self.repo.get_by_name("alice").id, 1)


class RepositoryUpdateTests(unittest.TestCase):

    def setUp(self):
        self.repo = DatabaseRepository(":memory:")
        self.addCleanup(self.repo._conn.close)
        self.repo.add(1, "alice", "original message")

    def test_update_changes_message_and_returns_true(self):
        self.assertTrue(self.repo.update(1, "  edited message  "))
        self.assertEqual(self.repo.get_by_id(1).message, "edited message")

    def test_update_returns_false_for_unknown_id(self):
        self.assertFalse(self.repo.update(999, "edited message"))
        self.assertEqual(self.repo.get_by_id(1).message, "original message")

    def test_update_rejects_negative_id(self):
        with self.assertRaises(Exception) as ctx:
            self.repo.update(-1, "edited message")
        self.assertEqual(str(ctx.exception), "Negative ID")

    def test_update_rejects_empty_message(self):
        for bad in (None, "", "    "):
            with self.subTest(new_message=bad):
                with self.assertRaises(Exception) as ctx:
                    self.repo.update(1, bad)
                self.assertEqual(str(ctx.exception), "Empty message")
        self.assertEqual(self.repo.get_by_id(1).message, "original message")

    def test_update_rejects_non_int_id(self):
        with self.assertRaises(Exception) as ctx:
            self.repo.update("abc", "edited message")
        self.assertEqual(str(ctx.exception), "Not an int ID")


class ScraperTests(unittest.TestCase):
    @patch("src.scraper.requests.get")
    def test_successful_request_returns_contents(self, mock_get):
        response = Mock()
        response.text = "<html>ok</html>"
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        out = scrape_page(URL)

        self.assertIsInstance(out, HTMLScraperOutput)
        self.assertTrue(out.success)
        self.assertEqual(out.contents, "<html>ok</html>")
        mock_get.assert_called_once_with(URL, impersonate="chrome", timeout=10)

    @patch("src.scraper.requests.get")
    def test_network_error_returns_failure_output(self, mock_get):
        mock_get.side_effect = RequestsError("DNS failure")

        out = scrape_page(URL)

        self.assertFalse(out.success)
        self.assertIn(f"Failed to fetch {URL}", out.contents)
        self.assertIn("DNS failure", out.contents)

    @patch("src.scraper.requests.get")
    def test_http_error_status_returns_failure_output(self, mock_get):
        response = Mock()
        response.raise_for_status.side_effect = RequestsError("403 Forbidden")
        mock_get.return_value = response

        out = scrape_page(URL)

        self.assertFalse(out.success)
        self.assertIn("403", out.contents)


class ParserTests(unittest.TestCase):
    def test_parses_all_messages_with_ids_names_and_texts(self):
        page = make_board([(101, "alice", "first post", None),
                           (202, "bob", "second post", None)])

        comments = parse_page(page)

        self.assertEqual(
            comments,
            [Comment(name="alice", message="first post", id=101),
             Comment(name="bob", message="second post", id=202)],
        )

    def test_signature_is_appended_to_message(self):
        page = make_board([(1, "alice", "hello", "-- sent from my toaster")])

        comment = parse_page(page)[0]

        self.assertTrue(comment.message.startswith("hello"))
        self.assertIn("Signature: -- sent from my toaster", comment.message)

    def test_page_without_messages_returns_empty_list(self):
        self.assertEqual(parse_page("<html><body><p>nothing here</p></body></html>"), [])

    def test_ignores_cells_that_are_not_messages(self):
        page = make_board([(7, "alice", "real message", None)]).replace(
            "</tr>", '<td class="author">not a message</td></tr>'
        )

        comments = parse_page(page)

        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0].id, 7)


class ParserFixtureTests(unittest.TestCase):
    def setUp(self):
        self.comments = parse_page(FIXTURE.read_text(encoding="utf-8"))

    def test_real_page_yields_valid_comments(self):
        self.assertGreater(len(self.comments), 0)
        for c in self.comments:
            with self.subTest(comment_id=c.id):
                self.assertIsInstance(c, Comment)
                self.assertIsInstance(c.id, int)
                self.assertGreater(c.id, 0)
                self.assertTrue(c.name.strip())
                self.assertTrue(c.message.strip())

    def test_real_page_message_ids_are_unique(self):
        ids = [c.id for c in self.comments]
        self.assertEqual(len(ids), len(set(ids)))


class MapperTests(unittest.TestCase):
    def test_saves_every_comment_with_positional_args(self):
        repo = Mock(spec=DBRInterface)
        comments = [Comment(name="alice", message="one", id=1),
                    Comment(name="bob", message="two", id=2)]

        save_to_db(comments, repo)

        self.assertEqual(repo.add.call_args_list,
                         [call(1, "alice", "one"), call(2, "bob", "two")])

    def test_skips_non_comment_objects(self):
        repo = Mock(spec=DBRInterface)

        save_to_db([Comment(name="alice", message="one", id=1), "junk", None, 42], repo)

        repo.add.assert_called_once_with(1, "alice", "one")

    def test_empty_list_does_not_touch_repository(self):
        repo = Mock(spec=DBRInterface)
        save_to_db([], repo)
        repo.add.assert_not_called()

    def test_round_trip_into_real_repository(self):
        repo = DatabaseRepository(":memory:")
        self.addCleanup(repo._conn.close)

        save_to_db([Comment(name="alice", message=" one ", id=1)], repo)

        self.assertEqual(repo.get_by_id(1), Comment(name="alice", message="one", id=1))


class ControllerScenarioTests(unittest.TestCase):
    def setUp(self):
        self.repo = Mock(spec=DBRInterface)
        self.log = Mock(spec=logging.Logger)
        self.controller = ForumParserContoller(self.repo, self.log)
        # _last_run is class state shared by every test -> make cooldown expired
        ForumParserContoller._last_run = time.monotonic() - ForumParserContoller.cooldown - 1
        self.addCleanup(setattr, ForumParserContoller, "_last_run", 0.0)
        self.comment = Comment(name="alice", message="hi", id=1)

    @patch("src.controller.scrape_page")
    @patch("src.controller.parse_page")
    @patch("src.controller.save_to_db")
    def test_successful_scenario_scrapes_parses_and_saves(self, m_save, m_parse, m_scrape):
        m_scrape.return_value = HTMLScraperOutput(success=True, contents="<html>page</html>")
        m_parse.return_value = [self.comment]

        self.controller.run(URL)

        m_scrape.assert_called_once_with(URL)
        m_parse.assert_called_once_with("<html>page</html>")
        m_save.assert_called_once_with([self.comment], self.repo)
        self.log.warning.assert_not_called()
        self.log.error.assert_not_called()
        self.assertIn("successfully finished", self.log.info.call_args.args[0])

    @patch("src.controller.scrape_page")
    @patch("src.controller.parse_page")
    @patch("src.controller.save_to_db")
    def test_cooldown_blocks_run_and_nothing_is_called(self, m_save, m_parse, m_scrape):
        ForumParserContoller._last_run = time.monotonic()  # ran just now

        self.controller.run(URL)

        m_scrape.assert_not_called()
        m_parse.assert_not_called()
        m_save.assert_not_called()
        self.log.warning.assert_called_once()
        self.assertIn("cooldown active", self.log.warning.call_args.args[0])

    @patch("src.controller.scrape_page")
    @patch("src.controller.parse_page")
    @patch("src.controller.save_to_db")
    def test_second_immediate_run_is_blocked_then_allowed_again(self, m_save, m_parse, m_scrape):
        m_scrape.return_value = HTMLScraperOutput(success=True, contents="<html/>")
        m_parse.return_value = [self.comment]

        self.controller.run(URL)
        self.controller.run(URL)  # too soon
        self.assertEqual(m_scrape.call_count, 1)
        self.assertIn("cooldown active", self.log.warning.call_args.args[0])

        ForumParserContoller._last_run -= ForumParserContoller.cooldown + 1  # time passes
        self.controller.run(URL)
        self.assertEqual(m_scrape.call_count, 2)

    @patch("src.controller.scrape_page")
    @patch("src.controller.parse_page")
    @patch("src.controller.save_to_db")
    def test_failed_scrape_stops_before_parsing(self, m_save, m_parse, m_scrape):
        m_scrape.return_value = HTMLScraperOutput(success=False, contents="Failed to fetch: 404")

        self.controller.run(URL)

        m_parse.assert_not_called()
        m_save.assert_not_called()
        self.log.warning.assert_called_once()
        self.assertIn("failed to scrape page", self.log.warning.call_args.args[0])

    @patch("src.controller.scrape_page")
    @patch("src.controller.parse_page")
    @patch("src.controller.save_to_db")
    def test_no_comments_found_stops_before_saving(self, m_save, m_parse, m_scrape):
        m_scrape.return_value = HTMLScraperOutput(success=True, contents="<html/>")
        m_parse.return_value = []

        self.controller.run(URL)

        m_save.assert_not_called()
        self.log.warning.assert_called_once()
        self.assertIn("couldn't find any comments", self.log.warning.call_args.args[0])

    @patch("src.controller.scrape_page")
    @patch("src.controller.parse_page")
    @patch("src.controller.save_to_db")
    def test_repository_exception_is_logged_and_swallowed(self, m_save, m_parse, m_scrape):
        m_scrape.return_value = HTMLScraperOutput(success=True, contents="<html/>")
        m_parse.return_value = [self.comment]
        m_save.side_effect = Exception("db is down")

        self.controller.run(URL)  # must not raise

        m_save.assert_called_once()
        self.log.error.assert_called_once()
        self.assertIn("db is down", self.log.error.call_args.args[0])


class EndToEndTests(unittest.TestCase):
    """Real parser + real repository + real network call."""

    def test_page_lands_in_database(self):
        html = FIXTURE.read_text(encoding="utf-8")

        repo = DatabaseRepository(":memory:")
        log = Mock(spec=logging.Logger)
        controller = ForumParserContoller(repo, log)
        ForumParserContoller._last_run = time.monotonic() - ForumParserContoller.cooldown - 1
        self.addCleanup(setattr, ForumParserContoller, "_last_run", 0.0)
        
        controller.run(URL)

        expected = parse_page(html)
        self.assertGreater(len(expected), 0)
        log.error.assert_not_called()
        for c in expected:
            with self.subTest(comment_id=c.id):
                stored = repo.get_by_id(c.id)
                self.assertIsNotNone(stored)
                self.assertEqual(stored.name, c.name.strip())
                self.assertEqual(stored.message, c.message.strip())


if __name__ == "__main__":
    unittest.main(verbosity=2)