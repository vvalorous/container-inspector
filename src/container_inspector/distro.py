# Copyright (c) nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/container-inspector/
#
# This software is licensed under the Apache License version 2.0.#
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at:
#     http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from os import path
import shlex

import attr

logger = logging.getLogger(__name__)
# un-comment these lines to enable logging
# logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
# logger.setLevel(logging.DEBUG)


def logger_debug(*args):
    return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))

"""
Utilities to detect the distro of a root filesystem (image or layer) and collect
useful details.

The main file of interest is: /etc/os-release
- https://www.freedesktop.org/software/systemd/man/os-release.html

"""


@attr.attributes
class Distro(object):
    """
    Configuration data. Shared definition as found in a layer json file and an image
    config json file.
    """

    os = attr.attrib(
        default='linux',
        metadata=dict(doc='Operating system, dafeulat to linux.')
    )

    architecture = attr.attrib(
        default=None,
        metadata=dict(doc='Processor architecture such as x86, x86_64, arm or amd64.')
    )

    name = attr.attrib(
        default='linux',
        metadata=dict(doc='''Based on os-release: https://www.freedesktop.org/software/systemd/man/os-release.html
            NAME= A string identifying the operating system, without a version component,
            and suitable for presentation to the user. If not set, defaults to "NAME=Linux".
            Example: "NAME=Fedora" or "NAME="Debian GNU/Linux"".
        ''')
    )

    version = attr.attrib(
        default=None,
        metadata=dict(doc='''Based on os-release: https://www.freedesktop.org/software/systemd/man/os-release.html
            VERSION= A string identifying the operating system version, excluding any OS
            name information, possibly including a release code name, and suitable for
            presentation to the user. This field is optional. Example: "VERSION=17" or
            "VERSION="17 (Beefy Miracle)"".
        ''')
    )

    identifier = attr.attrib(
        default='linux',
        metadata=dict(doc='''Based on os-release: https://www.freedesktop.org/software/systemd/man/os-release.html
            ID= A lower-case string (no spaces or other characters outside of 0–9, a–z, ".",
            "_" and "-") identifying the operating system, excluding any version information
            and suitable for processing by scripts or usage in generated filenames. If not
            set, defaults to "ID=linux". Example: "ID=fedora" or "ID=debian".
        ''')
    )

    id_like = attr.attrib(
        default=attr.Factory(list),
        metadata=dict(doc='''Based on os-release: https://www.freedesktop.org/software/systemd/man/os-release.html
            This is a list of ids, not a space-separated string.
            ID_LIKE= A space-separated list of operating system identifiers in the same
            syntax as the ID= setting. It should list identifiers of operating systems that
            are closely related to the local operating system in regards to packaging and
            programming interfaces, for example listing one or more OS identifiers the local
            OS is a derivative from. An OS should generally only list other OS identifiers
            it itself is a derivative of, and not any OSes that are derived from it, though
            symmetric relationships are possible. Build scripts and similar should check
            this variable if they need to identify the local operating system and the value
            of ID= is not recognized. Operating systems should be listed in order of how
            closely the local operating system relates to the listed ones, starting with the
            closest. This field is optional. Example: for an operating system with
            "ID=centos", an assignment of "ID_LIKE="rhel fedora"" would be appropriate. For
            an operating system with "ID=ubuntu", an assignment of "ID_LIKE=debian" is
            appropriate.
        ''')
    )

    version_codename = attr.attrib(
        default=None,
        metadata=dict(doc='''Based on os-release: https://www.freedesktop.org/software/systemd/man/os-release.html
            VERSION_CODENAME= A lower-case string (no spaces or other characters outside of
            0–9, a–z, ".", "_" and "-") identifying the operating system release code name,
            excluding any OS name information or release version, and suitable for
            processing by scripts or usage in generated filenames. This field is optional
            and may not be implemented on all systems. Examples: "VERSION_CODENAME=buster",
            "VERSION_CODENAME=xenial"
        ''')
    )

    version_id = attr.attrib(
        default=None,
        metadata=dict(doc='''Based on os-release: https://www.freedesktop.org/software/systemd/man/os-release.html
            VERSION_ID=A lower-case string (mostly numeric, no spaces or other characters
            outside of 0–9, a–z, ".", "_" and "-") identifying the operating system version,
            excluding any OS name information or release code name, and suitable for
            processing by scripts or usage in generated filenames. This field is optional.
            Example: "VERSION_ID=17" or "VERSION_ID=11.04".
        ''')
    )

    pretty_name = attr.attrib(
        default=None,
        metadata=dict(doc='''Based on os-release: https://www.freedesktop.org/software/systemd/man/os-release.html
            PRETTY_NAME=A pretty operating system name in a format suitable for presentation
            to the user. May or may not contain a release code name or OS version of some
            kind, as suitable. If not set, defaults to "PRETTY_NAME="Linux"". Example:
            "PRETTY_NAME="Fedora 17 (Beefy Miracle)"".
        ''')
    )

    cpe_name = attr.attrib(
        default=None,
        metadata=dict(doc='''Based on os-release: https://www.freedesktop.org/software/systemd/man/os-release.html
            CPE_NAME=A CPE name for the operating system, in URI binding syntax, following
            the Common Platform Enumeration Specification as proposed by the NIST. This
            field is optional. Example: "CPE_NAME="cpe:/o:fedoraproject:fedora:17""
        ''')
    )

    home_url = attr.attrib(
        default=None,
        metadata=dict(doc='''Based on os-release: https://www.freedesktop.org/software/systemd/man/os-release.html
            HOME_URL= should refer to the homepage of the operating system, or alternatively
            some homepage of the specific version of the operating system.
        ''')
    )

    documentation_url = attr.attrib(
        default=None,
        metadata=dict(doc='''Based on os-release: https://www.freedesktop.org/software/systemd/man/os-release.html
            DOCUMENTATION_URL= should refer to the main documentation page for this
            operating system.
        ''')
    )

    support_url = attr.attrib(
        default=None,
        metadata=dict(doc='''Based on os-release: https://www.freedesktop.org/software/systemd/man/os-release.html
            SUPPORT_URL= should refer to the main support page for the
            operating system, if there is any. This is primarily intended for operating
            systems which vendors provide support for.
        ''')
    )

    bug_report_url = attr.attrib(
        default=None,
        metadata=dict(doc='''Based on os-release: https://www.freedesktop.org/software/systemd/man/os-release.html
            BUG_REPORT_URL= should refer to the
            main bug reporting page for the operating system, if there is any. This is
            primarily intended for operating systems that rely on community QA.
        ''')
    )

    privacy_policy_url = attr.attrib(
        default=None,
        metadata=dict(doc='''Based on os-release: https://www.freedesktop.org/software/systemd/man/os-release.html
            PRIVACY_POLICY_URL= should refer to the main privacy policy page for the
            operating system, if there is any.
        ''')
    )

    build_id = attr.attrib(
        default=None,
        metadata=dict(doc='''Based on os-release: https://www.freedesktop.org/software/systemd/man/os-release.html
            BUILD_ID=A string uniquely identifying the system image used as the origin for a
            distribution (it is not updated with system updates). The field can be identical
            between different VERSION_IDs as BUILD_ID is an only a unique identifier to a
            specific version. Distributions that release each update as a new version would
            only need to use VERSION_ID as each build is already distinct based on the
            VERSION_ID. This field is optional. Example: "BUILD_ID="2013-03-20.3"" or
            "BUILD_ID=201303203".
        ''')
    )

    variant = attr.attrib(
        default=None,
        metadata=dict(doc='''Based on os-release: https://www.freedesktop.org/software/systemd/man/os-release.html
            VARIANT= A string identifying a specific variant or edition of the operating
            system suitable for presentation to the user. This field may be used to inform
            the user that the configuration of this system is subject to a specific
            divergent set of rules or default configuration settings. This field is optional
            and may not be implemented on all systems. Examples: "VARIANT="Server Edition"",
            "VARIANT="Smart Refrigerator Edition"" Note: this field is for display purposes
            only. The VARIANT_ID field should be used for making programmatic decisions.
        ''')
    )

    variant_id = attr.attrib(
        default=None,
        metadata=dict(doc='''Based on os-release: https://www.freedesktop.org/software/systemd/man/os-release.html
            VARIANT_ID= A lower-case string (no spaces or other characters outside of 0–9,
            a–z, ".", "_" and "-"), identifying a specific variant or edition of the
            operating system. This may be interpreted by other packages in order to
            determine a divergent default configuration. This field is optional and may not
            be implemented on all systems. Examples: "VARIANT_ID=server",
            "VARIANT_ID=embedded"
        ''')
    )

    logo = attr.attrib(
        default=None,
        metadata=dict(doc='''Based on os-release: https://www.freedesktop.org/software/systemd/man/os-release.html
            LOGO= A string, specifying the name of an icon as defined by freedesktop.org
            Icon Theme Specification. This can be used by graphical applications to display
            an operating system's or distributor's logo. This field is optional and may not
            necessarily be implemented on all systems. Examples: "LOGO=fedora-logo", "LOGO
            =distributor-logo-opensuse"
        ''')
    )

    extra_data = attr.attrib(
        default=attr.Factory(dict),
        metadata=dict(doc='''A mapping of extra data key/value pairs''')
    )

    def is_debian_based(self):
        return (
            self.identifier == 'debian'
            or self.identifier == 'ubuntu'
            or (self.id_like and 'debian' in (self.id_like or '')) 
        )

    def to_dict(self):
        return attr.asdict(self)

    @classmethod
    def from_file(cls, location):
        """
        Return a Distro built from an os-release file.
        """

        data = parse_os_release(location) or {}
        kwargs = dict(
            # This idiom looks a tad wierd but we want to always get a linux as
            # default even if the poped value is an empty string or None
            os=data.pop('OS', 'linux') or 'linux',
            name=data.pop('NAME', 'linux') or 'linux',
            identifier=data.pop('ID', 'linux') or 'linux',

            architecture=data.pop('ARCHITECTURE', None),
            version=data.pop('VERSION', None),
            id_like=data.pop('ID_LIKE', None),
            version_codename=data.pop('VERSION_CODENAME', None),
            version_id=data.pop('VERSION_ID', None),
            pretty_name=data.pop('PRETTY_NAME', None),
            cpe_name=data.pop('CPE_NAME', None),
            home_url=data.pop('HOME_URL', None),
            documentation_url=data.pop('DOCUMENTATION_URL', None),
            support_url=data.pop('SUPPORT_URL', None),
            bug_report_url=data.pop('BUG_REPORT_URL', None),
            privacy_policy_url=data.pop('PRIVACY_POLICY_URL', None),
            build_id=data.pop('BUILD_ID', None),
            variant=data.pop('VARIANT', None),
            variant_id=data.pop('VARIANT_ID', None),
            logo=data.pop('LOGO', None),
        )

        # ignored this
        data.pop('ANSI_COLOR', None)

        # note: we poped all known key/value pairs above.
        # therefore the remainder are unknown, extra data.
        if data:
            kwargs['extra_data'] = data

        return cls(**kwargs)

    @classmethod
    def from_rootfs(cls, location):
        """
        Return a Distro built from an os-release file in the root filesystem at
        `location`.
        """
        for candidate_path in ('etc/os-release', 'usr/lib/os-release',):
            os_release = path.join(location, candidate_path)
            if path.exists(os_release):
                return cls.from_file(os_release)


def parse_os_release(location):
    """
    Return a mapping built from an os-release-like file at `location`.

    See https://www.linux.org/docs/man5/os-release.html

    $ cat /etc/os-release
    NAME="Ubuntu"
    VERSION="16.04.6 LTS (Xenial Xerus)"
    ID=ubuntu
    ID_LIKE=debian
    PRETTY_NAME="Ubuntu 16.04.6 LTS"
    VERSION_ID="16.04"
    HOME_URL="http://www.ubuntu.com/"
    SUPPORT_URL="http://help.ubuntu.com/"
    BUG_REPORT_URL="http://bugs.launchpad.net/ubuntu/"
    VERSION_CODENAME=xenial
    UBUNTU_CODENAME=xenial

    Note the /etc/lsb-release file has the same format, but different tags.
    """
    with open(location) as osrl:
        lines = (line.strip() for line in osrl)
        lines = (line.partition('=') for line in lines if line and not line.startswith('#'))
        return {key.strip(): ''.join(shlex.split(value)) for key, _, value in lines}


def get_debian_details():
    """
    See /etc/dpkg/origins/ for Debian distro.
    See /etc/apt/sources.list
    """
    pass


def get_alpine_details():
    """
    arch is in  /etc/apk/arch
    release is in /etc/alpine-release
    See /etc/apk/repositories to get a list of base repo URLS
    """


def get_rpm_details():
    """
    On RH-based distro: /etc/yum.repos.d/  dir contains the "*.repo" files with
    repos baseurl.
    /etc/redhat-release contains a version
    """


def get_fedora_details():
    """
    One Fedora see also:
    /usr/lib/swidtag/fedoraproject.org/ may contains SWID tag files
    /usr/lib/fedora-release: bare release name
    /usr/lib/system-release-cpe: bare cpe

    /usr/lib/os-release : main os-release
    extra os release tags:
        REDHAT_BUGZILLA_PRODUCT="Fedora"
        REDHAT_BUGZILLA_PRODUCT_VERSION=rawhide
        REDHAT_SUPPORT_PRODUCT="Fedora"
        REDHAT_SUPPORT_PRODUCT_VERSION=rawhide

    rpmdb is sqlite on FC33 and up:
        /var/lib/rpm/rpmdb.sqlite
    before it is bdb
    """


def get_suse_details():
    """
    Reccent version use ndb for RPM db
    /usr/lib/sysimage/rpm/
    and
    /usr/lib/os-release
    Repos are listed in:
    /etc/zypp/repos.d/ directory

    /etc/products.d/openSUSE.prod is an XML file with many details
    """


def get_rhel_details():
    """
    Use switags like fedora
    /usr/lib/swidtag/redhat.com/com.redhat.RHEL-8.0-x86_64.swidtag
    /usr/lib/swidtag/redhat.com/com.redhat.RHEL-8-x86_64.swidtag
    """


def get_centos_details():
    """
    /etc/centos-release :one line of release info
    /etc/centos-release-upstream : one line of data on the RHEL thsi is based on
    /etc/os-release has a few extra fields
        CENTOS_MANTISBT_PROJECT="CentOS-8"
        CENTOS_MANTISBT_PROJECT_VERSION="8"
        REDHAT_SUPPORT_PRODUCT="centos"
        REDHAT_SUPPORT_PRODUCT_VERSION="8"

    /etc/system-release-cpe : the cpe (also in os-release)

    presence of /usr/share/doc/centos-release-5/ dir may help for older centos
    """


def get_distroless_details():
    """
    The presence of /var/lib/dpkg/status.d/ dir with one Package-like file for each
    installed file replaces using a /var/lib/dpkg/status file.

    /etc/os-release is the file to check for for details
    There are no apt sources and no dpkg/info details
    the /usr/lib/os-release is that of upstream Debian

    PRETTY_NAME="Distroless"
    NAME="Debian GNU/Linux"
    ID="debian"
    VERSION_ID="9"
    VERSION="Debian GNU/Linux 9 (stretch)"
    HOME_URL="https://github.com/GoogleContainerTools/distroless"
    SUPPORT_URL="https://github.com/GoogleContainerTools/distroless/blob/master/README.md"
    BUG_REPORT_URL="https://github.com/GoogleContainerTools/distroless/issues/new"
    """


def get_busybox_details():
    """
    A bare byusybox-based image has a base layer with only busybox
    So we can find about the /bin/[' exe and the '/bin/busybox' ... one of them
    should contain these strings
    "Usage: busybox"
    "Licensed under GPLv2"
    as a string line: "BusyBox v1.22.1 (Ubuntu 1:1.22.0-15ubuntu1.4)"
    and no /etc/os-release and only one executable and
    /etc/group
    /etc/localtime
    /etc/passwd
    /etc/shadow
    """
