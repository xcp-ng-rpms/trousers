%global package_speccommit 22bdbb8331bae164b910be4f2ba7fceef709d99c
%global usver 0.3.15
%global xsver 1
%global xsrel %{xsver}%{?xscount}%{?xshash}
Name: trousers
Summary: TCG's Software Stack v1.2
Version: 0.3.15
Release: %{?xsrel}%{?dist}
License: BSD
Url: http://trousers.sourceforge.net

Source0: trousers-0.3.15.tar.gz
Source1: tcsd.service
Patch0: trousers-0.3.14-noinline.patch
Patch1: trousers-0.3.14-unlock-in-err-path.patch
Patch2: trousers-0.3.14-fix-indent-obj_policy.patch
Patch3: trousers-0.3.14-fix-indent-tspi_key.patch

BuildRequires: make
BuildRequires: libtool openssl-devel gettext-devel autoconf automake
BuildRequires: systemd
Requires(pre): shadow-utils
# remove systemd dependency for flatpak builds
%if ! 0%{?flatpak}
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
%endif
Requires: %{name}-lib%{?_isa} = %{version}-%{release}

%description
TrouSerS is an implementation of the Trusted Computing Group's Software Stack
(TSS) specification. You can use TrouSerS to write applications that make use
of your TPM hardware. TPM hardware can create, store and use RSA keys
securely (without ever being exposed in memory), verify a platform's software
state using cryptographic hashes and more.

%package lib
Summary: TrouSerS libtspi library
# Needed obsoletes due to the -lib subpackage split
Obsoletes: trousers < 0.3.13-4

%description lib
The libtspi library for use in Trusted Computing enabled applications.

%package static
Summary: TrouSerS TCG Device Driver Library
Requires: %{name}-devel%{?_isa} = %{version}-%{release}

%description static
The TCG Device Driver Library (TDDL) used by the TrouSerS tcsd as the
interface to the TPM's device driver. For more information about writing
applications to the TDDL interface, see the latest TSS spec at
https://www.trustedcomputinggroup.org/specs/TSS.

%package devel
Summary: TrouSerS header files and documentation
Requires: %{name}-lib%{?_isa} = %{version}-%{release}

%description devel
Header files and man pages for use in creating Trusted Computing enabled
applications.

%prep
%autosetup -p1
# fix man page paths
sed -i -e 's|/var/tpm|/var/lib/tpm|g' -e 's|/usr/local/var|/var|g' man/man5/tcsd.conf.5.in man/man8/tcsd.8.in

%build
chmod +x ./bootstrap.sh
./bootstrap.sh
%configure --with-gui=openssl
make -k %{?_smp_mflags}

%install
mkdir -p %{buildroot}%{_localstatedir}/lib/tpm
%make_install
find %{buildroot} -type f -name '*.la' -print -delete
mkdir -p %{buildroot}%{_unitdir}
install -Dpm0644 %{SOURCE1} %{buildroot}%{_unitdir}/

%pre
getent group tss >/dev/null || groupadd -f -g 59 -r tss
if ! getent passwd tss >/dev/null ; then
    if ! getent passwd 59 >/dev/null ; then
      useradd -r -u 59 -g tss -d /dev/null -s /sbin/nologin -c "Account used for TPM access" tss
    else
      useradd -r -g tss -d /dev/null -s /sbin/nologin -c "Account used for TPM access" tss
    fi
fi
exit 0

%post
%systemd_post tcsd.service

%preun
%systemd_preun tcsd.service

%postun
%systemd_postun_with_restart tcsd.service

%files
%doc README ChangeLog
%{_sbindir}/tcsd
%config(noreplace) %attr(0640, root, tss) %{_sysconfdir}/tcsd.conf
%{_mandir}/man5/*
%{_mandir}/man8/*
%attr(644,root,root) %{_unitdir}/tcsd.service
%attr(0700, tss, tss) %{_localstatedir}/lib/tpm/

%files lib
%license LICENSE
%{_libdir}/libtspi.so.1*

%files devel
# The files to be used by developers, 'trousers-devel'
%doc doc/LTC-TSS_LLD_08_r2.pdf doc/TSS_programming_SNAFUs.txt
%attr(0755, root, root) %{_libdir}/libtspi.so
%{_includedir}/tss/
%{_includedir}/trousers/
%{_mandir}/man3/Tspi_*

%files static
# The only static library shipped by trousers, the TDDL
%{_libdir}/libtddl.a

%changelog
* Mon Jun 17 2024 Stephen Cheng <stephen.cheng@cloud.com> - 0.3.15-1
- First imported release

