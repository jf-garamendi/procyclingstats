import argparse

from procyclingstats.__main__ import get_corresponding_scraping_class

from .fixtures_utils import FixturesUtils
from .scraper_test_base_class import method_test


def configure_parser() -> argparse.ArgumentParser:
    """
    Configures the parser and parses the arguments.

    :return: Configured arguments parser ready to parse arguments.
    """
    parser = argparse.ArgumentParser(
        prog="python -m tests",
        description="CLI for modifiing tests fixtures.")

    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--quiet", action="store_true",
        help="Turns off logging.")
    subparsers = parser.add_subparsers(help="Command types available.",
        dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Adds HTML and data " +
        "fixture created from given URL to fixtures directory.")
    add_parser.add_argument("urls", metavar="url", type=str, nargs="+",
        help="Absolute or relative URLs of PCS pages which HTML and parsed " +
        "data should be copied to .txt and .json file with name of given URL.")

    add_html_parser = subparsers.add_parser("add_html",
        help="Adds HTML fixture created from given URL to fixtures directory.")
    add_html_parser.add_argument("urls", metavar="url", type=str, nargs="+",
        help="Absolute or relative URLs of PCS pages which HTML should be " +
        "copied to .txt file with name of given URL.")

    subparsers.add_parser("update_htmls", help="Updates HTML fixtures " +
        "from fixtures directory if parsing results of old HTML differ to " +
        "parsing results of the current one.")

    return parser


def run(args: argparse.Namespace, fixturer_path: str = "./tests/fixtures/"):
    f_utils = FixturesUtils(fixturer_path)
    if args.command in ("add", "add_html"):
        for url in args.urls:
            ScraperClass = get_corresponding_scraping_class(url)
            obj = ScraperClass(url)
            filename = f_utils.url_to_filename(
                obj.relative_url())

            if args.command == "add":
                if not args.quiet:
                    print(f"Adding: {filename}.txt")
                f_utils.make_html_fixture(obj)
                if not args.quiet:
                    print(f"Adding: {filename}.json")
                f_utils.make_data_fixture(obj)

            elif args.command == "add_html":
                if not args.quiet:
                    print(f"Adding: {filename}.txt")
                f_utils.make_html_fixture(obj)

    elif args.command == "update_htmls":
        urls = f_utils.get_urls_from_fixtures_dir("txt")
        for url in urls:
            print(url)
            ScraperClass = get_corresponding_scraping_class(url)
            # create scraping object from both old and new HTML
            new_scraper_obj = ScraperClass(url)
            old_html = f_utils.get_html_fixture(new_scraper_obj.relative_url())
            old_scraper_obj = ScraperClass(url, old_html, False)

            try:
                parsed_obj1 = new_scraper_obj.parse()
                parsed_obj2 = old_scraper_obj.parse()
            except Exception as e:
                print(f"Exception raised: {url}")
                raise(e)
            update_needed = False
            for method in parsed_obj1.keys():
                try:
                    method_test(parsed_obj1[method], parsed_obj2[method])
                except AssertionError:
                    update_needed = True

            if update_needed:
                if not args.quiet:
                    print(f"Updating: {f_utils.url_to_filename(url)}.txt")
                f_utils.make_html_fixture(new_scraper_obj)
            else:
                if not args.quiet:
                    print("HTML up to date: " +
                        f"{f_utils.url_to_filename(url)}.txt")

if __name__ == "__main__":
    parser_args = configure_parser().parse_args()
    run(parser_args)
