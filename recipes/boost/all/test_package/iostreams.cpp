#include <boost/iostreams/device/file_descriptor.hpp>

#if defined(BOOST_NAMESPACE)
namespace boost = BOOST_NAMESPACE;
#endif

#ifdef WITH_ZLIB
#include <boost/iostreams/filter/zlib.hpp>
int check_zlib_link() {
    boost::iostreams::zlib_error error(0);
    return error.error();
}
#endif

#ifdef WITH_BZIP2
#include <boost/iostreams/filter/bzip2.hpp>
int check_bzip2_link() {
    boost::iostreams::bzip2_error error(0);
    return error.error();
}
#endif

#ifdef WITH_LZMA
#include <boost/iostreams/filter/lzma.hpp>
int check_lzma_link() {
    boost::iostreams::lzma_error error(0);
    return error.error();
}
#endif

#ifdef WITH_ZSTD
#include <boost/iostreams/filter/zstd.hpp>
int check_zstd_link() {
    boost::iostreams::zstd_error error(0);
    return error.error();
}
#endif

int main() {
    #ifdef WITH_ZLIB
    if (check_zlib_link() != 0) {
        return -1;
    }
    #endif
    #ifdef WITH_BZIP2
    if (check_bzip2_link() != 0) {
        return -2;
    }
    #endif
    #ifdef WITH_LZMA
    if (check_lzma_link() != 0) {
        return -3;
    }
    #endif
    #ifdef WITH_ZSTD
    if (check_zstd_link() != 0) {
        return -4;
    }
    #endif

    boost::iostreams::file_descriptor fd;
    return static_cast<int>(fd.is_open());
}
