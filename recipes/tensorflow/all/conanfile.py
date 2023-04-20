from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import collect_libs, copy, get, mkdir, rename, rm
from conan.tools.microsoft import is_msvc, VCVars
from io import StringIO
import os


required_conan_version = ">=1.47.0"


class TensorflowConan(ConanFile):
    name = "tensorflow"
    description = "The core open source library to help you develop and train ML models"
    license = "Apache-2.0"
    url = "https://github.com/Nekto89/conan-center-index"
    homepage = "https://www.tensorflow.org"
    topics = (
        "machine-learning",
        "deep-neural-networks",
        "deep-learning",
        "neural-network",
        "ml",
        "distributed",
    )
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        pass

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def validate(self):
        if self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration(f"{self.ref} supports only x86_64")

    def source(self):
        pass

    def generate(self):
        if is_msvc(self):
            ms = VCVars(self)
            ms.generate()

    def build(self):
        get(
            self,
            **self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)],
            strip_root=False,
        )
        if is_msvc(self):
            #add version to dll name and regenerate *.lib file
            rm(self, "*.lib", os.path.join(self.build_folder, "lib"), recursive=True)
            mkdir(self, os.path.join(self.build_folder, "bin"))
            old_tensorflow_dll = os.path.join(self.build_folder, "lib", "tensorflow.dll")
            new_tensorflow_dll = os.path.join(self.build_folder, "bin", f"tensorflow-{self.version}.dll")
            rename(self, old_tensorflow_dll, new_tensorflow_dll)

            #dump all symbols that are exported from dll to *.exp
            dumpbin_result = StringIO()
            self.run(
                f'"dumpbin.exe" "/EXPORTS" "{new_tensorflow_dll}"',
                output=dumpbin_result,
                env="conanbuild",
            )
            dumpbin_output = dumpbin_result.getvalue()
            dumpbin_result.close()
            dumpbin_output = dumpbin_output[
                dumpbin_output.find(
                    "name",
                    dumpbin_output.find(
                        "RVA",
                        dumpbin_output.find("hint", dumpbin_output.find("ordinal")),
                    ),
                )
                + 4 :
            ].lstrip()

            exports_file = os.path.join(self.build_folder, f"tensorflow-{self.version}.exp")
            with open(exports_file, "w", encoding="utf-8") as f:
                f.write("EXPORTS\n")
                for line in dumpbin_output.splitlines():
                    splitted_line = line.split()
                    if len(splitted_line) > 3:
                        f.write(splitted_line[3] + "\n")
            new_tensorflow_lib = os.path.join(self.build_folder, "lib", f"tensorflow-{self.version}.lib")
            #generate *.lib file from *.exp
            self.run(
                f'"lib.exe" "/def:{exports_file}" "/OUT:{new_tensorflow_lib}" "/MACHINE:X64"',
                env="conanbuild",
            )

            # https://github.com/tensorflow/tensorflow/issues/58707
            # copy missing headers from linux package
            get(
                self,
                **self.conan_data["sources"][self.version]["Linux"][str(self.settings.arch)],
                strip_root=False,
                destination="linux",
                pattern="include/tensorflow/*",
            )
            rename(
                self,
                src=os.path.join(
                    self.build_folder,
                    "linux",
                    "include",
                    "tensorflow",
                    "c",
                    "tf_buffer.h",
                ),
                dst=os.path.join(self.build_folder, "include", "tensorflow", "c", "tf_buffer.h"),
            )
            mkdir(
                self,
                os.path.join(self.build_folder, "include", "tensorflow", "tsl", "c"),
            )
            rename(
                self,
                src=os.path.join(
                    self.build_folder,
                    "linux",
                    "include",
                    "tensorflow",
                    "tsl",
                    "c",
                    "tsl_status.h",
                ),
                dst=os.path.join(
                    self.build_folder,
                    "include",
                    "tensorflow",
                    "tsl",
                    "c",
                    "tsl_status.h",
                ),
            )
            mkdir(
                self,
                os.path.join(self.build_folder, "include", "tensorflow", "tsl", "platform"),
            )
            rename(
                self,
                src=os.path.join(
                    self.build_folder,
                    "linux",
                    "include",
                    "tensorflow",
                    "tsl",
                    "platform",
                    "ctstring.h",
                ),
                dst=os.path.join(
                    self.build_folder,
                    "include",
                    "tensorflow",
                    "tsl",
                    "platform",
                    "ctstring.h",
                ),
            )
            rename(
                self,
                src=os.path.join(
                    self.build_folder,
                    "linux",
                    "include",
                    "tensorflow",
                    "tsl",
                    "platform",
                    "ctstring_internal.h",
                ),
                dst=os.path.join(
                    self.build_folder,
                    "include",
                    "tensorflow",
                    "tsl",
                    "platform",
                    "ctstring_internal.h",
                ),
            )

    def package(self):
        copy(
            self,
            pattern="LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        copy(
            self,
            pattern="THIRD_PARTY_TF_C_LICENSES",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        copy(
            self,
            pattern="*",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )
        if self.settings.os == "Windows":
            copy(
                self,
                pattern="*.lib",
                dst=os.path.join(self.package_folder, "lib"),
                src=os.path.join(self.source_folder, "lib"),
            )
            copy(
                self,
                pattern="*.dll",
                dst=os.path.join(self.package_folder, "bin"),
                src=os.path.join(self.source_folder, "bin"),
            )
        else:
            copy(
                self,
                pattern="*",
                dst=os.path.join(self.package_folder, "lib"),
                src=os.path.join(self.source_folder, "lib"),
            )

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.libs = collect_libs(self)
