from conans import ConanFile, CMake
from conans.util.files import save
import os
import sys

channel = os.getenv("CONAN_CHANNEL", "testing")
username = os.getenv("CONAN_USERNAME", "sourcedelica")
version_env = "CONAN_PACKAGE_VERSION"
version_str = os.getenv(version_env)
if not version_str:
    sys.stderr.write("%s not set\n" % version_env)
    sys.exit(1)


class CAFReuseConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    version = version_str
    requires = "caf/%s@%s/%s" % (version, username, channel)
    default_options = "caf:shared=False"
    generators = "cmake"

    def build(self):
        tests_dir = "tests"
        repo_url = "https://github.com/actor-framework/actor-framework.git"
        self.run("rm -rf %s" % tests_dir)
        self.run("git init %s" % tests_dir)
        self.run("cd %s && git remote add origin %s" % (tests_dir, repo_url))
        self.run("cd %s && git config core.sparseCheckout true" % tests_dir)
        save("%s/.git/info/sparse-checkout" % tests_dir, "libcaf_test")
        save("%s/.git/info/sparse-checkout" % tests_dir, "libcaf_core/test", True)
        save("%s/.git/info/sparse-checkout" % tests_dir, "libcaf_io/test", True)
        self.run("cd %s && git pull origin %s --depth 1" % (tests_dir, self.version))

        cmake = CMake(self.settings)
        self.run('cmake "%s" %s' % (self.conanfile_directory, cmake.command_line))
        self.run("cmake --build . %s" % cmake.build_config)

    def test(self):
        self.run(os.sep.join([".", "bin", "caf-test"]))
