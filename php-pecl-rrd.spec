# centos/sclo spec file for php-pecl-rrd, from:
#
# remipo spec file for php-pecl-rrd
# with SCL compatibility, from:
#
# Fedora spec file for php-pecl-rrd
#
# Copyright (c) 2011-2019 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/4.0/
#
# Please, preserve the changelog entries
#

%if 0%{?scl:1}
%global sub_prefix %{scl_prefix}
%if "%{scl}" == "rh-php72"
%global sub_prefix sclo-php72-
%endif
%if "%{scl}" == "rh-php73"
%global sub_prefix sclo-php73-
%endif
%scl_package        php-pecl-rrd
%endif

%global pecl_name rrd
%global ini_name  40-%{pecl_name}.ini

Summary:      PHP Bindings for rrdtool
Name:         %{?sub_prefix}php-pecl-rrd
Version:      2.0.1
Release:      1%{?dist}
License:      BSD
URL:          http://pecl.php.net/package/rrd

Source:       http://pecl.php.net/get/%{pecl_name}-%{version}%{?prever}.tgz

BuildRequires: %{?dtsprefix}gcc
BuildRequires: %{?scl_prefix}php-devel >= 7
BuildRequires: rrdtool
BuildRequires: pkgconfig(librrd) >= 1.3.0
BuildRequires: %{?scl_prefix}php-pear

Requires:     %{?scl_prefix}php(zend-abi) = %{php_zend_api}
Requires:     %{?scl_prefix}php(api) = %{php_core_api}

Conflicts:    %{?scl_prefix}rrdtool-php
Provides:     %{?scl_prefix}php-%{pecl_name}               = %{version}
Provides:     %{?scl_prefix}php-%{pecl_name}%{?_isa}       = %{version}
Provides:     %{?scl_prefix}php-pecl(%{pecl_name})         = %{version}
Provides:     %{?scl_prefix}php-pecl(%{pecl_name})%{?_isa} = %{version}
%if "%{?scl_prefix}" != "%{?sub_prefix}"
Provides:     %{?scl_prefix}php-pecl-%{pecl_name}          = %{version}-%{release}
Provides:     %{?scl_prefix}php-pecl-%{pecl_name}%{?_isa}  = %{version}-%{release}
%endif


%description
Procedural and simple OO wrapper for rrdtool - data logging and graphing
system for time series data.


%prep 
%setup -c -q

mv %{pecl_name}-%{version}%{?prever} NTS

# Don't install/register tests
sed -e 's/role="test"/role="src"/' \
    %{?_licensedir:-e '/LICENSE/s/role="doc"/role="src"/' } \
    -i package.xml

cd NTS
# Sanity check, really often broken
extver=$(sed -n '/#define PHP_RRD_VERSION/{s/.* "//;s/".*$//;p}' php_rrd.h)
if test "x${extver}" != "x%{version}%{?prever}"; then
   : Error: Upstream extension version is ${extver}, expecting %{version}%{?prever}.
   exit 1
fi
cd ..

cat > %{ini_name} << 'EOF'
; Enable %{pecl_name} extension module
extension=%{pecl_name}.so
EOF


%build
cd NTS
%{_bindir}/phpize
%configure --with-php-config=%{_bindir}/php-config
make %{?_smp_mflags}


%install
make install -C NTS INSTALL_ROOT=%{buildroot}

# Drop in the bit of configuration
install -D -m 644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

# Install XML package description
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

# Documentation
for i in $(grep 'role="doc"' package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 NTS/$i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


%check
%{__php} --no-php-ini \
    --define extension=%{buildroot}%{php_extdir}/%{pecl_name}.so \
    --modules | grep %{pecl_name}


cd NTS
if pkg-config librrd --atleast-version=1.5.0
then
  : ignore test failed with rrdtool gt 1.5
  rm tests/rrd_{016,017}.phpt
fi
if ! pkg-config librrd --atleast-version=1.4.0
then
  : ignore test failed with rrdtool lt 1.4
  rm tests/rrd_{012,017}.phpt
fi

make -C tests/data clean
make -C tests/data all

: upstream test suite for NTS extension
TEST_PHP_ARGS="-n -d extension=$PWD/modules/%{pecl_name}.so" \
REPORT_EXIT_STATUS=1 \
NO_INTERACTION=1 \
TEST_PHP_EXECUTABLE=%{_bindir}/php \
%{_bindir}/php -n \
   run-tests.php --show-diff


# when pear installed alone, after us
%triggerin -- %{?scl_prefix}php-pear
if [ -x %{__pecl} ] ; then
    %{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
fi

# posttrans as pear can be installed after us
%posttrans
if [ -x %{__pecl} ] ; then
    %{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
fi

%postun
if [ $1 -eq 0 -a -x %{__pecl} ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi


%files
%doc %{pecl_docdir}/%{pecl_name}
%{?_licensedir:%license NTS/LICENSE}
%{pecl_xmldir}/%{name}.xml

%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so


%changelog
* Thu Nov 14 2019 Remi Collet <remi@remirepo.net> - 2.0.1-1
- cleanup for centos/sclo

* Tue Sep 03 2019 Remi Collet <remi@remirepo.net> - 2.0.1-7
- rebuild for 7.4.0RC1

* Thu Aug 16 2018 Remi Collet <remi@remirepo.net> - 2.0.1-6
- rebuild for 7.3.0beta2 new ABI

* Wed Jul 18 2018 Remi Collet <remi@remirepo.net> - 2.0.1-5
- rebuild for 7.3.0alpha4 new ABI

* Tue Jul 18 2017 Remi Collet <remi@remirepo.net> - 2.0.1-4
- rebuild for PHP 7.2.0beta1 new API

* Thu Dec  1 2016 Remi Collet <remi@fedoraproject.org> - 2.0.1-3
- rebuild with PHP 7.1.0 GA

* Wed Sep 14 2016 Remi Collet <remi@fedoraproject.org> - 2.0.1-2
- rebuild for PHP 7.1 new API version

* Wed May 11 2016 Remi Collet <remi@fedoraproject.org> - 2.0.1-1
- update to 2.0.1 (no change)

* Sun Mar  6 2016 Remi Collet <remi@fedoraproject.org> - 2.0.0-2
- adapt for F24

* Mon Dec 28 2015 Remi Collet <remi@fedoraproject.org> - 2.0.0-1
- update to 2.0.0

* Tue Oct 13 2015 Remi Collet <remi@fedoraproject.org> - 2.0.0-0.7.beta3
- rebuild for PHP 7.0.0RC5 new API version

* Fri Sep 18 2015 Remi Collet <remi@fedoraproject.org> - 2.0.0-0.6.beta3
- F23 rebuild with rh_layout

* Wed Jul 22 2015 Remi Collet <remi@fedoraproject.org> - 2.0.0-0.5.beta3
- rebuild against php 7.0.0beta2

* Wed Jul  8 2015 Remi Collet <remi@fedoraproject.org> - 2.0.0-0.4.beta3
- rebuild against php 7.0.0beta1

* Sat Jun 27 2015 Remi Collet <remi@fedoraproject.org> - 2.0.0-0.3.beta3
- update to 2.0.0beta3
- drop upstream patches

* Wed Jun 24 2015 Remi Collet <remi@fedoraproject.org> - 2.0.0-0.2.beta2
- rebuild for "rh_layout" (php70)

* Tue Jun 16 2015 Remi Collet <remi@fedoraproject.org> - 2.0.0-0.1.beta2
- update to 2.0.0beta2
- raise dependency on php >= 7
- drop runtime dependency on pear, new scriptlets
- don't install test suite
- add some upstream patches, post-beta2

* Wed Dec 24 2014 Remi Collet <remi@fedoraproject.org> - 1.1.3-3.1
- Fedora 21 SCL mass rebuild

* Mon Aug 25 2014 Remi Collet <rcollet@redhat.com> - 1.1.3-3
- improve SCL build

* Wed Apr 16 2014 Remi Collet <remi@fedoraproject.org> - 1.1.3-2
- add numerical prefix to extension configuration file (php 5.6)

* Wed Jan 15 2014 Remi Collet <remi@fedoraproject.org> - 1.1.3-1
- Update to 1.1.3 (stable)

* Tue Jan 14 2014 Remi Collet <remi@fedoraproject.org> - 1.1.2-2
- fix upstream patch

* Tue Jan 14 2014 Remi Collet <remi@fedoraproject.org> - 1.1.2-1
- Update to 1.1.2 (stable)
- install doc in pecl doc_dir
- install tests in pecl test_dir
- adapt for SCL

* Mon Sep 09 2013 Remi Collet <remi@fedoraproject.org> - 1.1.1-1
- Update to 1.1.1

* Thu Jan 24 2013 Remi Collet <remi@fedoraproject.org> - 1.1.0-1.1
- also provides php-rrd

* Sun Aug 12 2012 Remi Collet <remi@fedoraproject.org> - 1.1.0-1
- Version 1.1.0 (stable), api 1.1.0 (stable)

* Tue Jul 31 2012 Remi Collet <remi@fedoraproject.org> - 1.0.5-4
- ignore test results (fails with rrdtool 1.4.7)

* Fri Nov 18 2011 Remi Collet <Fedora@FamilleCollet.com> 1.0.5-2
- build against php 5.4

* Fri Nov 18 2011 Remi Collet <Fedora@FamilleCollet.com> 1.0.5-1
- update to 1.0.5
- change license from PHP to BSD

* Sun Nov 13 2011 Remi Collet <remi@fedoraproject.org> - 1.0.5-0.3.RC2
- build against php 5.4

* Mon Oct 17 2011 Remi Collet <Fedora@FamilleCollet.com> 1.0.5-0.2.RC2
- update to 1.0.5RC2
- drop patch merged upstream

* Wed Oct 05 2011 Remi Collet <Fedora@FamilleCollet.com> 1.0.5-0.1.RC1
- update to 1.0.5RC1
- build ZTS extension
- patch for https://bugs.php.net/bug.php?id=59992

* Tue Aug 16 2011 Remi Collet <Fedora@FamilleCollet.com> 1.0.4-1
- Version 1.0.4 (stable) - API 1.0.4 (stable)
- fix filters

* Fri Apr 29 2011 Remi Collet <Fedora@FamilleCollet.com> 1.0.3-1
- Version 1.0.3 (stable) - API 1.0.3 (stable)
- no change in sources

* Wed Apr 20 2011 Remi Collet <Fedora@FamilleCollet.com> 1.0.2-1
- Version 1.0.2 (stable) - API 1.0.2 (stable)
- no change in sources

* Sat Apr 16 2011 Remi Collet <Fedora@FamilleCollet.com> 1.0.1-1
- Version 1.0.1 (stable) - API 1.0.1 (stable)
- no change in sources
- remove generated Changelog (only latest version, no real value)

* Tue Apr 12 2011 Remi Collet <Fedora@FamilleCollet.com> 1.0.0-1
- Version 1.0.0 (stable) - API 1.0.0 (stable)
- remove all patches merged by upstream

* Sat Mar 05 2011 Remi Collet <Fedora@FamilleCollet.com> 0.10.0-2
- improved patches
- implement rrd_strversion

* Fri Mar 04 2011 Remi Collet <Fedora@FamilleCollet.com> 0.10.0-1
- Version 0.10.0 (stable) - API 0.10.0 (beta)
- remove patches, merged upstream
- add links to 5 new upstream bugs

* Mon Jan 03 2011 Remi Collet <Fedora@FamilleCollet.com> 0.9.0-1
- Version 0.9.0 (beta) - API 0.9.0 (beta)
- initial RPM

