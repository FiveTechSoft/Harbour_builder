/* $NetBSD: isnanl.c,v 1.8 2011/06/05 14:43:13 christos Exp $   */

/*
 * Copyright (c) 1992, 1993
 *  The Regents of the University of California.  All rights reserved.
 *
 * This software was developed by the Computer Systems Engineering group
 * at Lawrence Berkeley Laboratory under DARPA contract BG 91-66 and
 * contributed to Berkeley.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. Neither the name of the University nor the names of its contributors
 *    may be used to endorse or promote products derived from this software
 *    without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 *
 * from: Header: isinf.c,v 1.1 91/07/08 19:03:34 torek Exp
 */

#include <math.h>

#define EXT_EXP_INFNAN  0x7fff
#define EXT_EXPBITS     15
#define EXT_FRACHBITS   16
#define SNG_EXP_INFNAN  255
#define DBL_EXP_INFNAN  2047

struct ieee_ext
{
   unsigned int      ext_sign:1;
   unsigned int      ext_exp:EXT_EXPBITS;
   unsigned int      ext_frach:EXT_FRACHBITS;
   unsigned int      ext_frachm;
   unsigned int      ext_fraclm;
   unsigned int      ext_fracl;
};

union ieee_ext_u
{
   long double       extu_ld;
   struct ieee_ext   extu_ext;
};

struct ieee_double
{
   unsigned int      dbl_sign:1;
   unsigned int      dbl_exp:11;
   unsigned int      dbl_frach:20;
   unsigned int      dbl_fracl;
};

// HB_EXTERN_BEGIN
extern int _isnanl( long double x );
extern int _finitel( long double d );
extern int _finite( double d );
// HB_EXTERN_END

/*
 * 7.12.3.4 isnan - test for a NaN
 *          IEEE 754 compatible 80-bit extended-precision Intel 386 version
 */

int _isnanl( long double x )
{
   union ieee_ext_u u;

   u.extu_ld = x;

   return u.extu_ext.ext_exp == EXT_EXP_INFNAN &&
          ( u.extu_ext.ext_frach & 0x80000000 ) != 0 &&
          ( u.extu_ext.ext_frach != 0x80000000 || u.extu_ext.ext_fracl != 0 );
}

int _finite( double d )
{
   struct ieee_double * p = ( struct ieee_double * ) &d;

   return p->dbl_exp != DBL_EXP_INFNAN;
}

int _finitel( long double d )
{
   struct ieee_double * p = ( struct ieee_double * ) &d;

   return p->dbl_exp != DBL_EXP_INFNAN;
}

// #endif
 