include ../common.am

pkglib_LTLIBRARIES =

pkglib_LTLIBRARIES += libfaux_job.la
libfaux_job_la_SOURCES = faux_job.c
libfaux_job_la_CFLAGS = $(SAMPLER_CFLAGS)
libfaux_job_la_LIBADD = $(SAMPLER_LIBADD)
libfaux_job_la_LDFLAGS = $(SAMPLER_LDFLAGS)

pkglib_LTLIBRARIES += libclock.la
libclock_la_SOURCES = clock.c
libclock_la_CFLAGS = $(SAMPLER_CFLAGS)
libclock_la_LIBADD = $(SAMPLER_LIBADD)
libclock_la_LDFLAGS = $(SAMPLER_LDFLAGS)

pkglib_LTLIBRARIES += libfaux_job_alt.la
libfaux_job_alt_la_SOURCES = faux_job_alt.c
libfaux_job_alt_la_CFLAGS = $(SAMPLER_CFLAGS)
libfaux_job_alt_la_LIBADD = $(SAMPLER_LIBADD)
libfaux_job_alt_la_LDFLAGS = $(SAMPLER_LDFLAGS)

pkglib_LTLIBRARIES += libgrptest.la
libgrptest_la_SOURCES = grptest.c
libgrptest_la_CFLAGS = $(SAMPLER_CFLAGS)
libgrptest_la_LIBADD = $(SAMPLER_LIBADD)
libgrptest_la_LDFLAGS = $(SAMPLER_LDFLAGS)

pkglib_LTLIBRARIES += libtest_sampler.la
libtest_sampler_la_SOURCES = test_sampler.c
libtest_sampler_la_CFLAGS = $(SAMPLER_CFLAGS)
libtest_sampler_la_LIBADD = $(SAMPLER_LIBADD)
libtest_sampler_la_LDFLAGS = $(SAMPLER_LDFLAGS)

EXTRA_DIST = README.md
