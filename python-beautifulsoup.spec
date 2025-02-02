# Copyright 2025 Wong Hoi Sing Edison <hswong3i@pantarei-design.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

%global debug_package %{nil}

%global source_date_epoch_from_changelog 0

Name: python-beautifulsoup
Epoch: 100
Version: 4.13.3
Release: 1%{?dist}
BuildArch: noarch
Summary: Screen-scraping library
License: MIT
URL: https://pypi.org/project/beautifulsoup4/#history
Source0: %{name}_%{version}.orig.tar.gz
BuildRequires: fdupes
BuildRequires: python-rpm-macros
BuildRequires: python3-devel
BuildRequires: python3-setuptools

%description
Beautiful Soup is a library that makes it easy to scrape information
from web pages. It sits atop an HTML or XML parser, providing Pythonic
idioms for iterating, searching, and modifying the parse tree.

%prep
%autosetup -T -c -n %{name}_%{version}-%{release}
tar -zx -f %{S:0} --strip-components=1 -C .

%build
%py3_build

%install
%py3_install
find %{buildroot}%{python3_sitelib} -type f -name '*.pyc' -exec rm -rf {} \;
fdupes -qnrps %{buildroot}%{python3_sitelib}

%check

%if 0%{?suse_version} > 1500
%package -n python%{python3_version_nodots}-beautifulsoup4
Summary: Screen-scraping library
Requires: python3
Requires: python3-soupsieve > 1.2
Requires: python3-typing-extensions >= 4.0.0
Provides: python3-beautifulsoup4 = %{epoch}:%{version}-%{release}
Provides: python3dist(beautifulsoup4) = %{epoch}:%{version}-%{release}
Provides: python%{python3_version}-beautifulsoup4 = %{epoch}:%{version}-%{release}
Provides: python%{python3_version}dist(beautifulsoup4) = %{epoch}:%{version}-%{release}
Provides: python%{python3_version_nodots}-beautifulsoup4 = %{epoch}:%{version}-%{release}
Provides: python%{python3_version_nodots}dist(beautifulsoup4) = %{epoch}:%{version}-%{release}

%description -n python%{python3_version_nodots}-beautifulsoup4
Beautiful Soup is a library that makes it easy to scrape information
from web pages. It sits atop an HTML or XML parser, providing Pythonic
idioms for iterating, searching, and modifying the parse tree.

%files -n python%{python3_version_nodots}-beautifulsoup4
%license LICENSE
%{python3_sitelib}/*
%endif

%if !(0%{?suse_version} > 1500)
%package -n python3-beautifulsoup4
Summary: Screen-scraping library
Requires: python3
Requires: python3-soupsieve > 1.2
Requires: python3-typing-extensions >= 4.0.0
Provides: python3-beautifulsoup4 = %{epoch}:%{version}-%{release}
Provides: python3dist(beautifulsoup4) = %{epoch}:%{version}-%{release}
Provides: python%{python3_version}-beautifulsoup4 = %{epoch}:%{version}-%{release}
Provides: python%{python3_version}dist(beautifulsoup4) = %{epoch}:%{version}-%{release}
Provides: python%{python3_version_nodots}-beautifulsoup4 = %{epoch}:%{version}-%{release}
Provides: python%{python3_version_nodots}dist(beautifulsoup4) = %{epoch}:%{version}-%{release}

%description -n python3-beautifulsoup4
Beautiful Soup is a library that makes it easy to scrape information
from web pages. It sits atop an HTML or XML parser, providing Pythonic
idioms for iterating, searching, and modifying the parse tree.

%files -n python3-beautifulsoup4
%license LICENSE
%{python3_sitelib}/*
%endif

%changelog
