from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"

class GDCMConan(ConanFile):
    name = "gdcm"
    topics = ("dicom", "images")
    homepage = "http://gdcm.sourceforge.net/"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-3-Clause"
    description = "Insight Segmentation and Registration Toolkit"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake", "cmake_find_package"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("charls/2.1.0")
        self.requires("expat/2.3.0")
        self.requires("json-c/0.15")
        if self.settings.os != 'Windows':
            self.requires("libuuid/1.0.3")
        #self.requires("libxml2/2.9.10") used only for building application
        self.requires("openjpeg/2.4.0")
        self.requires("openssl/1.1.1k")
        #self.requires("poppler/20.09.0") used only for building application
        self.requires("zlib/1.2.11")
        #papyrus3
        #socketxx
        #libjpeg 8/12/16

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["GDCM_BUILD_DOCBOOK_MANPAGES"] = "OFF"
        self._cmake.definitions["GDCM_BUILD_SHARED_LIBS"] = "ON" if self.options.shared else "OFF"

        self._cmake.definitions["GDCM_USE_SYSTEM_CHARLS"] = "ON"
        self._cmake.definitions["GDCM_USE_JPEGLS"] = "ON"
        self._cmake.definitions["GDCM_USE_SYSTEM_EXPAT"] = "ON"
        self._cmake.definitions["GDCM_USE_SYSTEM_JSON"] = "ON"
        self._cmake.definitions["GDCM_USE_SYSTEM_LIBXML2"] = "OFF" #used only for building application
        self._cmake.definitions["GDCM_USE_SYSTEM_LJPEG"] = "OFF" #not possible to build in 8/12/16 bits simultaneously 
        self._cmake.definitions["GDCM_USE_SYSTEM_OPENJPEG"] = "ON"
        self._cmake.definitions["GDCM_USE_SYSTEM_OPENSSL"] = "ON"
        self._cmake.definitions["GDCM_USE_SYSTEM_PAPYRUS3"] = "OFF" #not present in cci
        self._cmake.definitions["GDCM_USE_SYSTEM_POPPLER"] = "OFF" #used only for building application
        self._cmake.definitions["GDCM_USE_SYSTEM_SOCKETXX"] = "OFF" #not present in cci
        self._cmake.definitions["GDCM_USE_SYSTEM_UUID"] = "OFF" if self.settings.os == "Windows" else "ON"
        self._cmake.definitions["GDCM_USE_SYSTEM_ZLIB"] = "ON"
        
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("Copyright.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    @property
    def _cmake_module_dir(self):
        return os.path.join("lib", self._gdcm_subdir)

    @property 
    def _gdcm_subdir(self):
        v = tools.Version(self.version)
        return f"gdcm-{v.major}.{v.minor}"

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs.append(os.path.join("include", self._gdcm_subdir))
        self.cpp_info.build_modules = [os.path.join(self._cmake_module_dir, "UseGDCM.cmake")]
