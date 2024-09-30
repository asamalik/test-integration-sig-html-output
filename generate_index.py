#!/usr/bin/python3

import yaml, os, jinja2, sys


class TestResultsAnalyzer:

    def __init__(self):
        self.settings = {}

        self.settings["results_path"] = "results"

        self.test_results = {}

    
    def do_everything(self):
        self.load_test_results()
        self.generate_html_pages()


    def load_test_results(self):

        with open(os.path.join(self.settings["results_path"], "run.yaml"), "r") as file:
            run_data = yaml.safe_load(file)

        results = {}
        results["plans"] = {}
        results["passed"] = set()
        results["failed"] = set()


        for plan in run_data["plans"]:
            plan_path = plan.lstrip("/")

            results["plans"][plan_path] = {}
            results["plans"][plan_path]["tests"] = {}
            results["plans"][plan_path]["passed"] = set()
            results["plans"][plan_path]["failed"] = set()
            results["plans"][plan_path]["link"] = "{}/report/default-0/".format(plan_path)

            plan_results_path = os.path.join(self.settings["results_path"], plan_path, "execute", "results.yaml")

            with open(plan_results_path, "r") as file:
                results_data = yaml.safe_load(file)

            for result in results_data:
                if result["result"] == "pass":
                    results["passed"].add(result["name"])
                    results["plans"][plan_path]["passed"].add(result["name"])
                elif result["result"] == "fail":
                    results["failed"].add(result["name"])
                    results["plans"][plan_path]["failed"].add(result["name"])

                results["plans"][plan_path]["tests"][result["name"]] = {}
                results["plans"][plan_path]["tests"][result["name"]]["name"] = result["name"]
                results["plans"][plan_path]["tests"][result["name"]]["result"] = result["result"]

        self.test_results = results

    
    def generate_html_pages(self):
        # Create the jinja2 thingy
        template_loader = jinja2.FileSystemLoader(searchpath="./templates/")
        template_env = jinja2.Environment(
            loader=template_loader,
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.settings["jinja2_template_env"] = template_env

        # Get the main page out
        self._generate_index_html()

    
    def _generate_index_html(self):
        template_data = {
            "data": self.test_results
        }
        self._generate_html_page("index", template_data, "index")


    def _generate_html_page(self, template_name, template_data, page_name):
        log("Generating the '{page_name}' page...".format(
            page_name=page_name
        ))

        template_env = self.settings["jinja2_template_env"]

        template = template_env.get_template("{template_name}.html".format(
            template_name=template_name
        ))

        page = template.render(**template_data)

        filename = ("{page_name}.html".format(
            page_name=page_name.replace(":", "--")
        ))

        log("  Writing file...  ({filename})".format(
            filename=filename
        ))
        with open(os.path.join(self.settings["results_path"], filename), "w") as file:
            file.write(page)
        
        log("  Done!")
        log("")


def log(msg):
    print(msg, file=sys.stderr)


def main():
    analyzer = TestResultsAnalyzer()
    analyzer.do_everything()


if __name__ == "__main__":
    main()