import pathlib
import re
import unittest


WORKFLOW = pathlib.Path(__file__).resolve().parents[2] / ".github/workflows/ci.yml"
RUNNER_CONTEXT = re.compile(r"\$\{\{\s*runner\.")


def invalid_job_env_lines(workflow):
    """Find runner expressions where GitHub does not make runner available."""
    in_job_env = False
    for number, line in enumerate(workflow.splitlines(), 1):
        indent = len(line) - len(line.lstrip(" "))
        if indent == 4 and line.strip() == "env:":
            in_job_env = True
            continue
        if indent <= 4 and line.strip() and not line.lstrip().startswith("#"):
            in_job_env = False
        if in_job_env and RUNNER_CONTEXT.search(line):
            yield number


class WorkflowContextTests(unittest.TestCase):
    def test_runner_context_is_absent_from_job_env(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertEqual([], list(invalid_job_env_lines(workflow)))
        self.assertIn("        env:\n          IM_GO_CONFIG_DIR: ${{ runner.temp }}/im-go-config", workflow)
        self.assertIn('Add-Content -Path $env:GITHUB_ENV -Value "IM_GO_CONFIG_DIR=$env:IM_GO_CONFIG_DIR"', workflow)

    def test_rejects_runner_context_at_deploy_job_env(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        invalid = workflow.replace(
            "  deploy:\n    needs: classify",
            "  deploy:\n    env:\n      IM_GO_CONFIG_DIR: ${{ runner.temp }}/im-go-config\n    needs: classify",
            1,
        )
        self.assertNotEqual(workflow, invalid)
        self.assertTrue(list(invalid_job_env_lines(invalid)))


if __name__ == "__main__":
    unittest.main()
