#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2014-2019, Matthew Brennan Jones <matthew.brennan.jones@gmail.com>
# Py-cpuinfo gets CPU info with pure Python 2 & 3
# It uses the MIT License
# It is hosted at: https://github.com/workhorsy/py-cpuinfo
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

CPUINFO_VERSION = (5, 0, 0)

import os, sys
import platform
import multiprocessing
import ctypes

try:
	import _winreg as winreg
except ImportError as err:
	try:
		import winreg
	except ImportError as err:
		pass

IS_PY2 = sys.version_info[0] == 2


class DataSource(object):
	bits = platform.architecture()[0]
	cpu_count = multiprocessing.cpu_count()
	is_windows = platform.system().lower() == 'windows'
	raw_arch_string = platform.machine()
	raw_uname_string = platform.uname()[5]
	can_cpuid = True

	@staticmethod
	def has_proc_cpuinfo():
		return os.path.exists('/proc/cpuinfo')

	@staticmethod
	def has_dmesg():
		return len(_program_paths('dmesg')) > 0

	@staticmethod
	def has_var_run_dmesg_boot():
		uname = platform.system().strip().strip('"').strip("'").strip().lower()
		return 'linux' in uname and os.path.exists('/var/run/dmesg.boot')

	@staticmethod
	def has_cpufreq_info():
		return len(_program_paths('cpufreq-info')) > 0

	@staticmethod
	def has_sestatus():
		return len(_program_paths('sestatus')) > 0

	@staticmethod
	def has_sysctl():
		return len(_program_paths('sysctl')) > 0

	@staticmethod
	def has_isainfo():
		return len(_program_paths('isainfo')) > 0

	@staticmethod
	def has_kstat():
		return len(_program_paths('kstat')) > 0

	@staticmethod
	def has_sysinfo():
		return len(_program_paths('sysinfo')) > 0

	@staticmethod
	def has_lscpu():
		return len(_program_paths('lscpu')) > 0

	@staticmethod
	def has_ibm_pa_features():
		return len(_program_paths('lsprop')) > 0

	@staticmethod
	def has_wmic():
		returncode, output = _run_and_get_stdout(['wmic', 'os', 'get', 'Version'])
		return returncode == 0 and len(output) > 0

	@staticmethod
	def cat_proc_cpuinfo():
		return _run_and_get_stdout(['cat', '/proc/cpuinfo'])

	@staticmethod
	def cpufreq_info():
		return _run_and_get_stdout(['cpufreq-info'])

	@staticmethod
	def sestatus_allow_execheap():
		return _run_and_get_stdout(['sestatus', '-b'], ['grep', '-i', '"allow_execheap"'])[1].strip().lower().endswith('on')

	@staticmethod
	def sestatus_allow_execmem():
		return _run_and_get_stdout(['sestatus', '-b'], ['grep', '-i', '"allow_execmem"'])[1].strip().lower().endswith('on')

	@staticmethod
	def dmesg_a():
		return _run_and_get_stdout(['dmesg', '-a'])

	@staticmethod
	def cat_var_run_dmesg_boot():
		return _run_and_get_stdout(['cat', '/var/run/dmesg.boot'])

	@staticmethod
	def sysctl_machdep_cpu_hw_cpufrequency():
		return _run_and_get_stdout(['sysctl', 'machdep.cpu', 'hw.cpufrequency'])

	@staticmethod
	def isainfo_vb():
		return _run_and_get_stdout(['isainfo', '-vb'])

	@staticmethod
	def kstat_m_cpu_info():
		return _run_and_get_stdout(['kstat', '-m', 'cpu_info'])

	@staticmethod
	def sysinfo_cpu():
		return _run_and_get_stdout(['sysinfo', '-cpu'])

	@staticmethod
	def lscpu():
		return _run_and_get_stdout(['lscpu'])

	@staticmethod
	def ibm_pa_features():
		import glob

		ibm_features = glob.glob('/proc/device-tree/cpus/*/ibm,pa-features')
		if ibm_features:
			return _run_and_get_stdout(['lsprop', ibm_features[0]])

	@staticmethod
	def wmic_cpu():
		return _run_and_get_stdout(['wmic', 'cpu', 'get', 'Name,CurrentClockSpeed,L2CacheSize,L3CacheSize,Description,Caption,Manufacturer', '/format:list'])

	@staticmethod
	def winreg_processor_brand():
		key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Hardware\Description\System\CentralProcessor\0")
		processor_brand = winreg.QueryValueEx(key, "ProcessorNameString")[0]
		winreg.CloseKey(key)
		return processor_brand

	@staticmethod
	def winreg_vendor_id():
		key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Hardware\Description\System\CentralProcessor\0")
		vendor_id = winreg.QueryValueEx(key, "VendorIdentifier")[0]
		winreg.CloseKey(key)
		return vendor_id

	@staticmethod
	def winreg_raw_arch_string():
		key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment")
		raw_arch_string = winreg.QueryValueEx(key, "PROCESSOR_ARCHITECTURE")[0]
		winreg.CloseKey(key)
		return raw_arch_string

	@staticmethod
	def winreg_hz_actual():
		key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Hardware\Description\System\CentralProcessor\0")
		hz_actual = winreg.QueryValueEx(key, "~Mhz")[0]
		winreg.CloseKey(key)
		hz_actual = _to_decimal_string(hz_actual)
		return hz_actual

	@staticmethod
	def winreg_feature_bits():
		key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Hardware\Description\System\CentralProcessor\0")
		feature_bits = winreg.QueryValueEx(key, "FeatureSet")[0]
		winreg.CloseKey(key)
		return feature_bits


def _program_paths(program_name):
	paths = []
	exts = filter(None, os.environ.get('PATHEXT', '').split(os.pathsep))
	path = os.environ['PATH']
	for p in os.environ['PATH'].split(os.pathsep):
		p = os.path.join(p, program_name)
		if os.access(p, os.X_OK):
			paths.append(p)
		for e in exts:
			pext = p + e
			if os.access(pext, os.X_OK):
				paths.append(pext)
	return paths

def _run_and_get_stdout(command, pipe_command=None):
	from subprocess import Popen, PIPE

	if not pipe_command:
		p1 = Popen(command, stdout=PIPE, stderr=PIPE, stdin=PIPE)
		output = p1.communicate()[0]
		if not IS_PY2:
			output = output.decode(encoding='UTF-8')
		return p1.returncode, output
	else:
		p1 = Popen(command, stdout=PIPE, stderr=PIPE, stdin=PIPE)
		p2 = Popen(pipe_command, stdin=p1.stdout, stdout=PIPE, stderr=PIPE)
		p1.stdout.close()
		output = p2.communicate()[0]
		if not IS_PY2:
			output = output.decode(encoding='UTF-8')
		return p2.returncode, output

# Make sure we are running on a supported system
def _check_arch():
	arch, bits = _parse_arch(DataSource.raw_arch_string)
	if not arch in ['X86_32', 'X86_64', 'ARM_7', 'ARM_8', 'PPC_64']:
		raise Exception("py-cpuinfo currently only works on X86 and some PPC and ARM CPUs.")

def _obj_to_b64(thing):
	import pickle
	import base64

	a = thing
	b = pickle.dumps(a)
	c = base64.b64encode(b)
	d = c.decode('utf8')
	return d

def _b64_to_obj(thing):
	import pickle
	import base64

	try:
		a = base64.b64decode(thing)
		b = pickle.loads(a)
		return b
	except:
		return {}

def _utf_to_str(input):
	if IS_PY2 and isinstance(input, unicode):
		return input.encode('utf-8')
	elif isinstance(input, list):
		return [_utf_to_str(element) for element in input]
	elif isinstance(input, dict):
		return {_utf_to_str(key): _utf_to_str(value)
			for key, value in input.items()}
	else:
		return input

def _copy_new_fields(info, new_info):
	keys = [
		'vendor_id', 'hardware', 'brand', 'hz_advertised', 'hz_actual',
		'hz_advertised_raw', 'hz_actual_raw', 'arch', 'bits', 'count',
		'raw_arch_string', 'raw_uname_string',
		'l2_cache_size', 'l2_cache_line_size', 'l2_cache_associativity',
		'stepping', 'model', 'family',
		'processor_type', 'extended_model', 'extended_family', 'flags',
		'l3_cache_size', 'l1_data_cache_size', 'l1_instruction_cache_size'
	]

	for key in keys:
		if new_info.get(key, None) and not info.get(key, None):
			info[key] = new_info[key]
		elif key == 'flags' and new_info.get('flags'):
			for f in new_info['flags']:
				if f not in info['flags']: info['flags'].append(f)
			info['flags'].sort()

def _get_field_actual(cant_be_number, raw_string, field_names):
	for line in raw_string.splitlines():
		for field_name in field_names:
			field_name = field_name.lower()
			if ':' in line:
				left, right = line.split(':', 1)
				left = left.strip().lower()
				right = right.strip()
				if left == field_name and len(right) > 0:
					if cant_be_number:
						if not right.isdigit():
							return right
					else:
						return right

	return None

def _get_field(cant_be_number, raw_string, convert_to, default_value, *field_names):
	retval = _get_field_actual(cant_be_number, raw_string, field_names)

	# Convert the return value
	if retval and convert_to:
		try:
			retval = convert_to(retval)
		except:
			retval = default_value

	# Return the default if there is no return value
	if retval is None:
		retval = default_value

	return retval

def _to_decimal_string(ticks):
	try:
		# Convert to string
		ticks = '{0}'.format(ticks)

		# Strip off non numbers and decimal places
		ticks = "".join(n for n in ticks if n.isdigit() or n=='.').strip()
		if ticks == '':
			ticks = '0'

		# Add decimal if missing
		if '.' not in ticks:
			ticks = '{0}.0'.format(ticks)

		# Remove trailing zeros
		ticks = ticks.rstrip('0')

		# Add one trailing zero for empty right side
		if ticks.endswith('.'):
			ticks = '{0}0'.format(ticks)

		# Make sure the number can be converted to a float
		ticks = float(ticks)
		ticks = '{0}'.format(ticks)
		return ticks
	except:
		return '0.0'

def _to_raw_hz(ticks, scale):
	try:
		# Make sure the number can be converted to a float
		ticks = float(ticks)
		ticks = '{0}'.format(ticks)

		# Scale the numbers
		hz = ticks.lstrip('0')
		old_index = hz.index('.')
		hz = hz.replace('.', '')
		hz = hz.ljust(scale + old_index+1, '0')
		new_index = old_index + scale
		hz = '{0}.{1}'.format(hz[:new_index], hz[new_index:])
		left, right = hz.split('.')
		left, right = int(left), int(right)
		return (left, right)
	except:
		return (0, 0)

def _parse_hz(hz_string):
	try:
		hz_string = hz_string.strip().lower()
		scale, hz = (None, None)

		if hz_string.endswith('ghz'):
			scale = 9
		elif hz_string.endswith('mhz'):
			scale = 6
		elif hz_string.endswith('hz'):
			scale = 1

		hz = "".join(n for n in hz_string if n.isdigit() or n=='.').strip()
		if not '.' in hz:
			hz += '.0'
		print('!!!!!!!! hz', (hz, scale, hz_string))
		hz, scale = _to_raw_hz(hz, scale)
		print('!!!!!!!! hz', (hz, scale, hz_string))

		return (scale, hz)
	except:
		return (0, 0)

def _to_friendly_hz(ticks, scale):
	try:
		# Get the raw Hz as a string
		left, right = _to_raw_hz(ticks, scale)
		result = '{0}.{1}'.format(left, right)

		# Get the location of the dot, and remove said dot
		dot_index = result.index('.')
		result = result.replace('.', '')

		# Get the Hz symbol and scale
		symbol = "Hz"
		scale = 0
		if dot_index > 9:
			symbol = "GHz"
			scale = 9
		elif dot_index > 6:
			symbol = "MHz"
			scale = 6
		elif dot_index > 3:
			symbol = "KHz"
			scale = 3

		# Get the Hz with the dot at the new scaled point
		result = '{0}.{1}'.format(result[:-scale-1], result[-scale-1:])

		# Format the ticks to have 4 numbers after the decimal
		# and remove any superfluous zeroes.
		result = '{0:.4f} {1}'.format(float(result), symbol)
		result = result.rstrip('0')
		return result
	except:
		return '0.0000 Hz'

def _to_friendly_bytes(input):
	import re

	if not input:
		return input
	input = "{0}".format(input)

	formats = {
		r"^[0-9]+B$" : 'B',
		r"^[0-9]+K$" : 'KB',
		r"^[0-9]+M$" : 'MB',
		r"^[0-9]+G$" : 'GB'
	}

	for pattern, friendly_size in formats.items():
		if re.match(pattern, input):
			return "{0} {1}".format(input[ : -1].strip(), friendly_size)

	return input

def _get_hz_string_from_brand(processor_brand):
	# Just return 0 if the processor brand does not have the Hz
	if not 'hz' in processor_brand.lower():
		return (1, '0.0')

	hz_brand = processor_brand.lower()
	scale = 1

	if hz_brand.endswith('mhz'):
		scale = 6
	elif hz_brand.endswith('ghz'):
		scale = 9
	if '@' in hz_brand:
		hz_brand = hz_brand.split('@')[1]
	else:
		hz_brand = hz_brand.rsplit(None, 1)[1]

	hz_brand = hz_brand.rstrip('mhz').rstrip('ghz').strip()
	hz_brand = _to_decimal_string(hz_brand)

	return (scale, hz_brand)

def _parse_cpu_string(cpu_string):
	import re

	# Find all the strings inside brackets ()
	starts = [m.start() for m in re.finditer('\(', cpu_string)]
	ends = [m.start() for m in re.finditer('\)', cpu_string)]
	print('!!! starts: ', starts)
	print('!!! ends: ', ends)
	insides = {k: v for k, v in zip(starts, ends)}
	print('!!!!!!!!!!!!!!!!! insides: ', insides)
	insides = [cpu_string[start+1 : end] for start, end in insides.items()]
	print('!!!!!!!!!!!!!!!!! insides: ', insides)

	# Find all the fields
	vendor_id, stepping, model, family = (None, None, None, None)
	for inside in insides:
		for pair in inside.split(','):
			pair = [n.strip() for n in pair.split(':')]
			if len(pair) > 1:
				name, value = pair[0], pair[1]
				if name == 'origin':
					vendor_id = value.strip('"')
				elif name == 'stepping':
					stepping = int(value.lstrip('0x'), 16)
				elif name == 'model':
					model = int(value.lstrip('0x'), 16)
				elif name in ['fam', 'family']:
					family = int(value.lstrip('0x'), 16)
	print('!!!!!!!!!!!!!!!!! (vendor_id, stepping, model, family): ', (vendor_id, stepping, model, family))

	# Find the Processor Brand
	# Strip off extra strings in brackets at end
	processor_brand = cpu_string.strip()
	is_working = True
	while is_working:
		print('!!! looping ...')
		print('!!! processor_brand: ', (processor_brand,))
		is_working = False
		for inside in insides:
			full = "({0})".format(inside)
			print('!!! full: ', full)
			if processor_brand.endswith(full):
				processor_brand = processor_brand[ :-len(full)].strip()
				is_working = True
	print('!!! processor_brand: ', (processor_brand,))

	# Find the Hz in the brand string
	scale, hz_brand = _get_hz_string_from_brand(processor_brand)
	print('!!! scale, hz_brand: ', (scale, hz_brand))

	# Find Hz inside brackets () after the brand string
	if hz_brand == '0.0':
		for inside in insides:
			hz = inside
			for entry in ['GHz', 'MHz', 'Hz']:
				if entry in hz:
					hz = "CPU @ " + hz[ : hz.find(entry) + len(entry)]
					print("!!!!!!!!!!!!!!!!!!!! hz:", hz)
					scale, hz_brand = _get_hz_string_from_brand(hz)
					print("!!!!!!!!!!!!!!!!!!!! scale, hz_brand:", (scale, hz_brand))
					break

	return (processor_brand, hz_brand, scale, vendor_id, stepping, model, family)

def _parse_dmesg_output(output):
	try:
		# Get all the dmesg lines that might contain a CPU string
		lines = output.split(' CPU0:')[1:] + \
				output.split(' CPU1:')[1:] + \
				output.split(' CPU:')[1:] + \
				output.split('\nCPU0:')[1:] + \
				output.split('\nCPU1:')[1:] + \
				output.split('\nCPU:')[1:]
		lines = [l.split('\n')[0].strip() for l in lines]
		print('!!!! lines:', lines)

		# Convert the lines to CPU strings
		cpu_strings = [_parse_cpu_string(l) for l in lines]
		print('!!! cpu_strings:', cpu_strings)

		# Find the CPU string that has the most fields
		best_string = None
		highest_count = 0
		for cpu_string in cpu_strings:
			count = sum([n is not None for n in cpu_string])
			if count > highest_count:
				highest_count = count
				best_string = cpu_string
		print('!!!!! best_string:', best_string)

		# If no CPU string was found, return {}
		if not best_string:
			return {}

		processor_brand, hz_actual, scale, vendor_id, stepping, model, family = best_string
		print('!!! multiple ...', (processor_brand, hz_actual, scale, vendor_id, stepping, model, family))
		print('!!!!!!!!!!!!!!!! hz_actual:', hz_actual)

		# Origin
		if '  Origin=' in output:
			fields = output[output.find('  Origin=') : ].split('\n')[0]
			fields = fields.strip().split()
			fields = [n.strip().split('=') for n in fields]
			fields = [{n[0].strip().lower() : n[1].strip()} for n in fields]
			print('!!! fields: ', fields)
			#print('fields: ', fields)
			for field in fields:
				name = list(field.keys())[0]
				value = list(field.values())[0]
				#print('name:{0}, value:{1}'.format(name, value))
				if name == 'origin':
					vendor_id = value.strip('"')
				elif name == 'stepping':
					stepping = int(value.lstrip('0x'), 16)
				elif name == 'model':
					model = int(value.lstrip('0x'), 16)
				elif name in ['fam', 'family']:
					family = int(value.lstrip('0x'), 16)
		#print('FIELDS: ', (vendor_id, stepping, model, family))
		print('!!! multiple ...', (processor_brand, hz_actual, scale, vendor_id, stepping, model, family))

		# Features
		flag_lines = []
		for category in ['  Features=', '  Features2=', '  AMD Features=', '  AMD Features2=']:
			if category in output:
				flag_lines.append(output.split(category)[1].split('\n')[0])

		flags = []
		for line in flag_lines:
			line = line.split('<')[1].split('>')[0].lower()
			for flag in line.split(','):
				flags.append(flag)
		flags.sort()
		print('!!! flags:', flags)

		# Convert from GHz/MHz string to Hz
		scale, hz_advertised = _get_hz_string_from_brand(processor_brand)
		print('!!! (scale, hz_advertised)', (scale, hz_advertised))

		info = {
		'vendor_id' : vendor_id,
		'brand' : processor_brand,

		'stepping' : stepping,
		'model' : model,
		'family' : family,
		'flags' : flags
		}

		if hz_advertised and hz_advertised != '0.0':
			info['hz_advertised'] = _to_friendly_hz(hz_advertised, scale)
			info['hz_actual'] = _to_friendly_hz(hz_actual, scale)

		if hz_advertised and hz_advertised != '0.0':
			info['hz_advertised_raw'] = _to_raw_hz(hz_advertised, scale)
			info['hz_actual_raw'] = _to_raw_hz(hz_actual, scale)

		return {k: v for k, v in info.items() if v}
	except:
		raise
		pass

	return {}

def _parse_arch(raw_arch_string):
	import re

	arch, bits = None, None
	raw_arch_string = raw_arch_string.lower()

	# X86
	if re.match('^i\d86$|^x86$|^x86_32$|^i86pc$|^ia32$|^ia-32$|^bepc$', raw_arch_string):
		arch = 'X86_32'
		bits = 32
	elif re.match('^x64$|^x86_64$|^x86_64t$|^i686-64$|^amd64$|^ia64$|^ia-64$', raw_arch_string):
		arch = 'X86_64'
		bits = 64
	# ARM
	elif re.match('^armv8-a|aarch64$', raw_arch_string):
		arch = 'ARM_8'
		bits = 64
	elif re.match('^armv7$|^armv7[a-z]$|^armv7-[a-z]$|^armv6[a-z]$', raw_arch_string):
		arch = 'ARM_7'
		bits = 32
	elif re.match('^armv8$|^armv8[a-z]$|^armv8-[a-z]$', raw_arch_string):
		arch = 'ARM_8'
		bits = 32
	# PPC
	elif re.match('^ppc32$|^prep$|^pmac$|^powermac$', raw_arch_string):
		arch = 'PPC_32'
		bits = 32
	elif re.match('^powerpc$|^ppc64$|^ppc64le$', raw_arch_string):
		arch = 'PPC_64'
		bits = 64
	# SPARC
	elif re.match('^sparc32$|^sparc$', raw_arch_string):
		arch = 'SPARC_32'
		bits = 32
	elif re.match('^sparc64$|^sun4u$|^sun4v$', raw_arch_string):
		arch = 'SPARC_64'
		bits = 64

	return (arch, bits)

def _is_bit_set(reg, bit):
	mask = 1 << bit
	is_set = reg & mask > 0
	return is_set


class CPUID(object):
	def __init__(self):
		self.prochandle = None

		# Figure out if SE Linux is on and in enforcing mode
		self.is_selinux_enforcing = False

		# Just return if the SE Linux Status Tool is not installed
		if not DataSource.has_sestatus():
			return

		# Figure out if we can execute heap and execute memory
		can_selinux_exec_heap = DataSource.sestatus_allow_execheap()
		can_selinux_exec_memory = DataSource.sestatus_allow_execmem()
		self.is_selinux_enforcing = (not can_selinux_exec_heap or not can_selinux_exec_memory)

	def _asm_func(self, restype=None, argtypes=(), byte_code=[]):
		byte_code = bytes.join(b'', byte_code)
		address = None

		if DataSource.is_windows:
			# Allocate a memory segment the size of the byte code, and make it executable
			size = len(byte_code)
			# Alloc at least 1 page to ensure we own all pages that we want to change protection on
			if size < 0x1000: size = 0x1000
			MEM_COMMIT = ctypes.c_ulong(0x1000)
			PAGE_READWRITE = ctypes.c_ulong(0x4)
			pfnVirtualAlloc = ctypes.windll.kernel32.VirtualAlloc
			pfnVirtualAlloc.restype = ctypes.c_void_p
			address = pfnVirtualAlloc(None, ctypes.c_size_t(size), MEM_COMMIT, PAGE_READWRITE)
			if not address:
				raise Exception("Failed to VirtualAlloc")

			# Copy the byte code into the memory segment
			memmove = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t)(ctypes._memmove_addr)
			if memmove(address, byte_code, size) < 0:
				raise Exception("Failed to memmove")

			# Enable execute permissions
			PAGE_EXECUTE = ctypes.c_ulong(0x10)
			old_protect = ctypes.c_ulong(0)
			pfnVirtualProtect = ctypes.windll.kernel32.VirtualProtect
			res = pfnVirtualProtect(ctypes.c_void_p(address), ctypes.c_size_t(size), PAGE_EXECUTE, ctypes.byref(old_protect))
			if not res:
				raise Exception("Failed VirtualProtect")

			# Flush Instruction Cache
			# First, get process Handle
			if not self.prochandle:
				pfnGetCurrentProcess = ctypes.windll.kernel32.GetCurrentProcess
				pfnGetCurrentProcess.restype = ctypes.c_void_p
				self.prochandle = ctypes.c_void_p(pfnGetCurrentProcess())
			# Actually flush cache
			res = ctypes.windll.kernel32.FlushInstructionCache(self.prochandle, ctypes.c_void_p(address), ctypes.c_size_t(size))
			if not res:
				raise Exception("Failed FlushInstructionCache")
		else:
			# Allocate a memory segment the size of the byte code
			size = len(byte_code)
			pfnvalloc = ctypes.pythonapi.valloc
			pfnvalloc.restype = ctypes.c_void_p
			address = pfnvalloc(ctypes.c_size_t(size))
			if not address:
				raise Exception("Failed to valloc")

			# Mark the memory segment as writeable only
			if not self.is_selinux_enforcing:
				WRITE = 0x2
				if ctypes.pythonapi.mprotect(ctypes.c_void_p(address), size, WRITE) < 0:
					raise Exception("Failed to mprotect")

			# Copy the byte code into the memory segment
			if ctypes.pythonapi.memmove(ctypes.c_void_p(address), byte_code, ctypes.c_size_t(size)) < 0:
				raise Exception("Failed to memmove")

			# Mark the memory segment as writeable and executable only
			if not self.is_selinux_enforcing:
				WRITE_EXECUTE = 0x2 | 0x4
				if ctypes.pythonapi.mprotect(ctypes.c_void_p(address), size, WRITE_EXECUTE) < 0:
					raise Exception("Failed to mprotect")

		# Cast the memory segment into a function
		functype = ctypes.CFUNCTYPE(restype, *argtypes)
		fun = functype(address)
		return fun, address

	def _run_asm(self, *byte_code):
		# Convert the byte code into a function that returns an int
		restype = ctypes.c_uint32
		argtypes = ()
		func, address = self._asm_func(restype, argtypes, byte_code)

		# Call the byte code like a function
		retval = func()

		byte_code = bytes.join(b'', byte_code)
		size = ctypes.c_size_t(len(byte_code))

		# Free the function memory segment
		if DataSource.is_windows:
			MEM_RELEASE = ctypes.c_ulong(0x8000)
			ctypes.windll.kernel32.VirtualFree(ctypes.c_void_p(address), ctypes.c_size_t(0), MEM_RELEASE)
		else:
			# Remove the executable tag on the memory
			READ_WRITE = 0x1 | 0x2
			if ctypes.pythonapi.mprotect(ctypes.c_void_p(address), size, READ_WRITE) < 0:
				raise Exception("Failed to mprotect")

			ctypes.pythonapi.free(ctypes.c_void_p(address))

		return retval

	# FIXME: We should not have to use different instructions to
	# set eax to 0 or 1, on 32bit and 64bit machines.
	def _zero_eax(self):
		return (
			b"\x31\xC0"         # xor eax,eax
		)

	def _zero_ecx(self):
		return (
			b"\x31\xC9"         # xor ecx,ecx
		)
	def _one_eax(self):
		return (
			b"\xB8\x01\x00\x00\x00" # mov eax,0x1"
		)

	# http://en.wikipedia.org/wiki/CPUID#EAX.3D0:_Get_vendor_ID
	def get_vendor_id(self):
		# EBX
		ebx = self._run_asm(
			self._zero_eax(),
			b"\x0F\xA2"         # cpuid
			b"\x89\xD8"         # mov ax,bx
			b"\xC3"             # ret
		)

		# ECX
		ecx = self._run_asm(
			self._zero_eax(),
			b"\x0f\xa2"         # cpuid
			b"\x89\xC8"         # mov ax,cx
			b"\xC3"             # ret
		)

		# EDX
		edx = self._run_asm(
			self._zero_eax(),
			b"\x0f\xa2"         # cpuid
			b"\x89\xD0"         # mov ax,dx
			b"\xC3"             # ret
		)

		# Each 4bits is a ascii letter in the name
		vendor_id = []
		for reg in [ebx, edx, ecx]:
			for n in [0, 8, 16, 24]:
				vendor_id.append(chr((reg >> n) & 0xFF))
		vendor_id = ''.join(vendor_id)

		return vendor_id

	# http://en.wikipedia.org/wiki/CPUID#EAX.3D1:_Processor_Info_and_Feature_Bits
	def get_info(self):
		# EAX
		eax = self._run_asm(
			self._one_eax(),
			b"\x0f\xa2"         # cpuid
			b"\xC3"             # ret
		)

		# Get the CPU info
		stepping = (eax >> 0) & 0xF # 4 bits
		model = (eax >> 4) & 0xF # 4 bits
		family = (eax >> 8) & 0xF # 4 bits
		processor_type = (eax >> 12) & 0x3 # 2 bits
		extended_model = (eax >> 16) & 0xF # 4 bits
		extended_family = (eax >> 20) & 0xFF # 8 bits

		return {
			'stepping' : stepping,
			'model' : model,
			'family' : family,
			'processor_type' : processor_type,
			'extended_model' : extended_model,
			'extended_family' : extended_family
		}

	# http://en.wikipedia.org/wiki/CPUID#EAX.3D80000000h:_Get_Highest_Extended_Function_Supported
	def get_max_extension_support(self):
		# Check for extension support
		max_extension_support = self._run_asm(
			b"\xB8\x00\x00\x00\x80" # mov ax,0x80000000
			b"\x0f\xa2"             # cpuid
			b"\xC3"                 # ret
		)

		return max_extension_support

	# http://en.wikipedia.org/wiki/CPUID#EAX.3D1:_Processor_Info_and_Feature_Bits
	def get_flags(self, max_extension_support):
		# EDX
		edx = self._run_asm(
			self._one_eax(),
			b"\x0f\xa2"         # cpuid
			b"\x89\xD0"         # mov ax,dx
			b"\xC3"             # ret
		)

		# ECX
		ecx = self._run_asm(
			self._one_eax(),
			b"\x0f\xa2"         # cpuid
			b"\x89\xC8"         # mov ax,cx
			b"\xC3"             # ret
		)

		# Get the CPU flags
		flags = {
			'fpu' : _is_bit_set(edx, 0),
			'vme' : _is_bit_set(edx, 1),
			'de' : _is_bit_set(edx, 2),
			'pse' : _is_bit_set(edx, 3),
			'tsc' : _is_bit_set(edx, 4),
			'msr' : _is_bit_set(edx, 5),
			'pae' : _is_bit_set(edx, 6),
			'mce' : _is_bit_set(edx, 7),
			'cx8' : _is_bit_set(edx, 8),
			'apic' : _is_bit_set(edx, 9),
			#'reserved1' : _is_bit_set(edx, 10),
			'sep' : _is_bit_set(edx, 11),
			'mtrr' : _is_bit_set(edx, 12),
			'pge' : _is_bit_set(edx, 13),
			'mca' : _is_bit_set(edx, 14),
			'cmov' : _is_bit_set(edx, 15),
			'pat' : _is_bit_set(edx, 16),
			'pse36' : _is_bit_set(edx, 17),
			'pn' : _is_bit_set(edx, 18),
			'clflush' : _is_bit_set(edx, 19),
			#'reserved2' : _is_bit_set(edx, 20),
			'dts' : _is_bit_set(edx, 21),
			'acpi' : _is_bit_set(edx, 22),
			'mmx' : _is_bit_set(edx, 23),
			'fxsr' : _is_bit_set(edx, 24),
			'sse' : _is_bit_set(edx, 25),
			'sse2' : _is_bit_set(edx, 26),
			'ss' : _is_bit_set(edx, 27),
			'ht' : _is_bit_set(edx, 28),
			'tm' : _is_bit_set(edx, 29),
			'ia64' : _is_bit_set(edx, 30),
			'pbe' : _is_bit_set(edx, 31),

			'pni' : _is_bit_set(ecx, 0),
			'pclmulqdq' : _is_bit_set(ecx, 1),
			'dtes64' : _is_bit_set(ecx, 2),
			'monitor' : _is_bit_set(ecx, 3),
			'ds_cpl' : _is_bit_set(ecx, 4),
			'vmx' : _is_bit_set(ecx, 5),
			'smx' : _is_bit_set(ecx, 6),
			'est' : _is_bit_set(ecx, 7),
			'tm2' : _is_bit_set(ecx, 8),
			'ssse3' : _is_bit_set(ecx, 9),
			'cid' : _is_bit_set(ecx, 10),
			#'reserved3' : _is_bit_set(ecx, 11),
			'fma' : _is_bit_set(ecx, 12),
			'cx16' : _is_bit_set(ecx, 13),
			'xtpr' : _is_bit_set(ecx, 14),
			'pdcm' : _is_bit_set(ecx, 15),
			#'reserved4' : _is_bit_set(ecx, 16),
			'pcid' : _is_bit_set(ecx, 17),
			'dca' : _is_bit_set(ecx, 18),
			'sse4_1' : _is_bit_set(ecx, 19),
			'sse4_2' : _is_bit_set(ecx, 20),
			'x2apic' : _is_bit_set(ecx, 21),
			'movbe' : _is_bit_set(ecx, 22),
			'popcnt' : _is_bit_set(ecx, 23),
			'tscdeadline' : _is_bit_set(ecx, 24),
			'aes' : _is_bit_set(ecx, 25),
			'xsave' : _is_bit_set(ecx, 26),
			'osxsave' : _is_bit_set(ecx, 27),
			'avx' : _is_bit_set(ecx, 28),
			'f16c' : _is_bit_set(ecx, 29),
			'rdrnd' : _is_bit_set(ecx, 30),
			'hypervisor' : _is_bit_set(ecx, 31)
		}

		# Get a list of only the flags that are true
		flags = [k for k, v in flags.items() if v]

		# http://en.wikipedia.org/wiki/CPUID#EAX.3D7.2C_ECX.3D0:_Extended_Features
		if max_extension_support >= 7:
			# EBX
			ebx = self._run_asm(
				self._zero_ecx(),
				b"\xB8\x07\x00\x00\x00" # mov eax,7
				b"\x0f\xa2"         # cpuid
				b"\x89\xD8"         # mov ax,bx
				b"\xC3"             # ret
			)

			# ECX
			ecx = self._run_asm(
				self._zero_ecx(),
				b"\xB8\x07\x00\x00\x00" # mov eax,7
				b"\x0f\xa2"         # cpuid
				b"\x89\xC8"         # mov ax,cx
				b"\xC3"             # ret
			)

			# Get the extended CPU flags
			extended_flags = {
				#'fsgsbase' : _is_bit_set(ebx, 0),
				#'IA32_TSC_ADJUST' : _is_bit_set(ebx, 1),
				'sgx' : _is_bit_set(ebx, 2),
				'bmi1' : _is_bit_set(ebx, 3),
				'hle' : _is_bit_set(ebx, 4),
				'avx2' : _is_bit_set(ebx, 5),
				#'reserved' : _is_bit_set(ebx, 6),
				'smep' : _is_bit_set(ebx, 7),
				'bmi2' : _is_bit_set(ebx, 8),
				'erms' : _is_bit_set(ebx, 9),
				'invpcid' : _is_bit_set(ebx, 10),
				'rtm' : _is_bit_set(ebx, 11),
				'pqm' : _is_bit_set(ebx, 12),
				#'FPU CS and FPU DS deprecated' : _is_bit_set(ebx, 13),
				'mpx' : _is_bit_set(ebx, 14),
				'pqe' : _is_bit_set(ebx, 15),
				'avx512f' : _is_bit_set(ebx, 16),
				'avx512dq' : _is_bit_set(ebx, 17),
				'rdseed' : _is_bit_set(ebx, 18),
				'adx' : _is_bit_set(ebx, 19),
				'smap' : _is_bit_set(ebx, 20),
				'avx512ifma' : _is_bit_set(ebx, 21),
				'pcommit' : _is_bit_set(ebx, 22),
				'clflushopt' : _is_bit_set(ebx, 23),
				'clwb' : _is_bit_set(ebx, 24),
				'intel_pt' : _is_bit_set(ebx, 25),
				'avx512pf' : _is_bit_set(ebx, 26),
				'avx512er' : _is_bit_set(ebx, 27),
				'avx512cd' : _is_bit_set(ebx, 28),
				'sha' : _is_bit_set(ebx, 29),
				'avx512bw' : _is_bit_set(ebx, 30),
				'avx512vl' : _is_bit_set(ebx, 31),

				'prefetchwt1' : _is_bit_set(ecx, 0),
				'avx512vbmi' : _is_bit_set(ecx, 1),
				'umip' : _is_bit_set(ecx, 2),
				'pku' : _is_bit_set(ecx, 3),
				'ospke' : _is_bit_set(ecx, 4),
				#'reserved' : _is_bit_set(ecx, 5),
				'avx512vbmi2' : _is_bit_set(ecx, 6),
				#'reserved' : _is_bit_set(ecx, 7),
				'gfni' : _is_bit_set(ecx, 8),
				'vaes' : _is_bit_set(ecx, 9),
				'vpclmulqdq' : _is_bit_set(ecx, 10),
				'avx512vnni' : _is_bit_set(ecx, 11),
				'avx512bitalg' : _is_bit_set(ecx, 12),
				#'reserved' : _is_bit_set(ecx, 13),
				'avx512vpopcntdq' : _is_bit_set(ecx, 14),
				#'reserved' : _is_bit_set(ecx, 15),
				#'reserved' : _is_bit_set(ecx, 16),
				#'mpx0' : _is_bit_set(ecx, 17),
				#'mpx1' : _is_bit_set(ecx, 18),
				#'mpx2' : _is_bit_set(ecx, 19),
				#'mpx3' : _is_bit_set(ecx, 20),
				#'mpx4' : _is_bit_set(ecx, 21),
				'rdpid' : _is_bit_set(ecx, 22),
				#'reserved' : _is_bit_set(ecx, 23),
				#'reserved' : _is_bit_set(ecx, 24),
				#'reserved' : _is_bit_set(ecx, 25),
				#'reserved' : _is_bit_set(ecx, 26),
				#'reserved' : _is_bit_set(ecx, 27),
				#'reserved' : _is_bit_set(ecx, 28),
				#'reserved' : _is_bit_set(ecx, 29),
				'sgx_lc' : _is_bit_set(ecx, 30),
				#'reserved' : _is_bit_set(ecx, 31)
			}

			# Get a list of only the flags that are true
			extended_flags = [k for k, v in extended_flags.items() if v]
			flags += extended_flags

		# http://en.wikipedia.org/wiki/CPUID#EAX.3D80000001h:_Extended_Processor_Info_and_Feature_Bits
		if max_extension_support >= 0x80000001:
			# EBX
			ebx = self._run_asm(
				b"\xB8\x01\x00\x00\x80" # mov ax,0x80000001
				b"\x0f\xa2"         # cpuid
				b"\x89\xD8"         # mov ax,bx
				b"\xC3"             # ret
			)

			# ECX
			ecx = self._run_asm(
				b"\xB8\x01\x00\x00\x80" # mov ax,0x80000001
				b"\x0f\xa2"         # cpuid
				b"\x89\xC8"         # mov ax,cx
				b"\xC3"             # ret
			)

			# Get the extended CPU flags
			extended_flags = {
				'fpu' : _is_bit_set(ebx, 0),
				'vme' : _is_bit_set(ebx, 1),
				'de' : _is_bit_set(ebx, 2),
				'pse' : _is_bit_set(ebx, 3),
				'tsc' : _is_bit_set(ebx, 4),
				'msr' : _is_bit_set(ebx, 5),
				'pae' : _is_bit_set(ebx, 6),
				'mce' : _is_bit_set(ebx, 7),
				'cx8' : _is_bit_set(ebx, 8),
				'apic' : _is_bit_set(ebx, 9),
				#'reserved' : _is_bit_set(ebx, 10),
				'syscall' : _is_bit_set(ebx, 11),
				'mtrr' : _is_bit_set(ebx, 12),
				'pge' : _is_bit_set(ebx, 13),
				'mca' : _is_bit_set(ebx, 14),
				'cmov' : _is_bit_set(ebx, 15),
				'pat' : _is_bit_set(ebx, 16),
				'pse36' : _is_bit_set(ebx, 17),
				#'reserved' : _is_bit_set(ebx, 18),
				'mp' : _is_bit_set(ebx, 19),
				'nx' : _is_bit_set(ebx, 20),
				#'reserved' : _is_bit_set(ebx, 21),
				'mmxext' : _is_bit_set(ebx, 22),
				'mmx' : _is_bit_set(ebx, 23),
				'fxsr' : _is_bit_set(ebx, 24),
				'fxsr_opt' : _is_bit_set(ebx, 25),
				'pdpe1gp' : _is_bit_set(ebx, 26),
				'rdtscp' : _is_bit_set(ebx, 27),
				#'reserved' : _is_bit_set(ebx, 28),
				'lm' : _is_bit_set(ebx, 29),
				'3dnowext' : _is_bit_set(ebx, 30),
				'3dnow' : _is_bit_set(ebx, 31),

				'lahf_lm' : _is_bit_set(ecx, 0),
				'cmp_legacy' : _is_bit_set(ecx, 1),
				'svm' : _is_bit_set(ecx, 2),
				'extapic' : _is_bit_set(ecx, 3),
				'cr8_legacy' : _is_bit_set(ecx, 4),
				'abm' : _is_bit_set(ecx, 5),
				'sse4a' : _is_bit_set(ecx, 6),
				'misalignsse' : _is_bit_set(ecx, 7),
				'3dnowprefetch' : _is_bit_set(ecx, 8),
				'osvw' : _is_bit_set(ecx, 9),
				'ibs' : _is_bit_set(ecx, 10),
				'xop' : _is_bit_set(ecx, 11),
				'skinit' : _is_bit_set(ecx, 12),
				'wdt' : _is_bit_set(ecx, 13),
				#'reserved' : _is_bit_set(ecx, 14),
				'lwp' : _is_bit_set(ecx, 15),
				'fma4' : _is_bit_set(ecx, 16),
				'tce' : _is_bit_set(ecx, 17),
				#'reserved' : _is_bit_set(ecx, 18),
				'nodeid_msr' : _is_bit_set(ecx, 19),
				#'reserved' : _is_bit_set(ecx, 20),
				'tbm' : _is_bit_set(ecx, 21),
				'topoext' : _is_bit_set(ecx, 22),
				'perfctr_core' : _is_bit_set(ecx, 23),
				'perfctr_nb' : _is_bit_set(ecx, 24),
				#'reserved' : _is_bit_set(ecx, 25),
				'dbx' : _is_bit_set(ecx, 26),
				'perftsc' : _is_bit_set(ecx, 27),
				'pci_l2i' : _is_bit_set(ecx, 28),
				#'reserved' : _is_bit_set(ecx, 29),
				#'reserved' : _is_bit_set(ecx, 30),
				#'reserved' : _is_bit_set(ecx, 31)
			}

			# Get a list of only the flags that are true
			extended_flags = [k for k, v in extended_flags.items() if v]
			flags += extended_flags

		flags.sort()
		return flags

	# http://en.wikipedia.org/wiki/CPUID#EAX.3D80000002h.2C80000003h.2C80000004h:_Processor_Brand_String
	def get_processor_brand(self, max_extension_support):
		processor_brand = ""

		# Processor brand string
		if max_extension_support >= 0x80000004:
			instructions = [
				b"\xB8\x02\x00\x00\x80", # mov ax,0x80000002
				b"\xB8\x03\x00\x00\x80", # mov ax,0x80000003
				b"\xB8\x04\x00\x00\x80"  # mov ax,0x80000004
			]
			for instruction in instructions:
				# EAX
				eax = self._run_asm(
					instruction,  # mov ax,0x8000000?
					b"\x0f\xa2"   # cpuid
					b"\x89\xC0"   # mov ax,ax
					b"\xC3"       # ret
				)

				# EBX
				ebx = self._run_asm(
					instruction,  # mov ax,0x8000000?
					b"\x0f\xa2"   # cpuid
					b"\x89\xD8"   # mov ax,bx
					b"\xC3"       # ret
				)

				# ECX
				ecx = self._run_asm(
					instruction,  # mov ax,0x8000000?
					b"\x0f\xa2"   # cpuid
					b"\x89\xC8"   # mov ax,cx
					b"\xC3"       # ret
				)

				# EDX
				edx = self._run_asm(
					instruction,  # mov ax,0x8000000?
					b"\x0f\xa2"   # cpuid
					b"\x89\xD0"   # mov ax,dx
					b"\xC3"       # ret
				)

				# Combine each of the 4 bytes in each register into the string
				for reg in [eax, ebx, ecx, edx]:
					for n in [0, 8, 16, 24]:
						processor_brand += chr((reg >> n) & 0xFF)

		# Strip off any trailing NULL terminators and white space
		processor_brand = processor_brand.strip("\0").strip()

		return processor_brand

	# http://en.wikipedia.org/wiki/CPUID#EAX.3D80000006h:_Extended_L2_Cache_Features
	def get_cache(self, max_extension_support):
		cache_info = {}

		# Just return if the cache feature is not supported
		if max_extension_support < 0x80000006:
			return cache_info

		# ECX
		ecx = self._run_asm(
			b"\xB8\x06\x00\x00\x80"  # mov ax,0x80000006
			b"\x0f\xa2"              # cpuid
			b"\x89\xC8"              # mov ax,cx
			b"\xC3"                   # ret
		)

		cache_info = {
			'size_kb' : ecx & 0xFF,
			'line_size_b' : (ecx >> 12) & 0xF,
			'associativity' : (ecx >> 16) & 0xFFFF
		}

		return cache_info

	def get_ticks(self):
		retval = None

		if DataSource.bits == '32bit':
			# Works on x86_32
			restype = None
			argtypes = (ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint))
			get_ticks_x86_32, address = self._asm_func(restype, argtypes,
				[
				b"\x55",         # push bp
				b"\x89\xE5",     # mov bp,sp
				b"\x31\xC0",     # xor ax,ax
				b"\x0F\xA2",     # cpuid
				b"\x0F\x31",     # rdtsc
				b"\x8B\x5D\x08", # mov bx,[di+0x8]
				b"\x8B\x4D\x0C", # mov cx,[di+0xc]
				b"\x89\x13",     # mov [bp+di],dx
				b"\x89\x01",     # mov [bx+di],ax
				b"\x5D",         # pop bp
				b"\xC3"          # ret
				]
			)

			high = ctypes.c_uint32(0)
			low = ctypes.c_uint32(0)

			get_ticks_x86_32(ctypes.byref(high), ctypes.byref(low))
			retval = ((high.value << 32) & 0xFFFFFFFF00000000) | low.value
		elif DataSource.bits == '64bit':
			# Works on x86_64
			restype = ctypes.c_uint64
			argtypes = ()
			get_ticks_x86_64, address = self._asm_func(restype, argtypes,
				[
				b"\x48",         # dec ax
				b"\x31\xC0",     # xor ax,ax
				b"\x0F\xA2",     # cpuid
				b"\x0F\x31",     # rdtsc
				b"\x48",         # dec ax
				b"\xC1\xE2\x20", # shl dx,byte 0x20
				b"\x48",         # dec ax
				b"\x09\xD0",     # or ax,dx
				b"\xC3",         # ret
				]
			)
			retval = get_ticks_x86_64()

		return retval

	def get_raw_hz(self):
		import time

		start = self.get_ticks()

		time.sleep(1)

		end = self.get_ticks()

		ticks = (end - start)

		return ticks

def _actual_get_cpu_info_from_cpuid(queue):
	'''
	Warning! This function has the potential to crash the Python runtime.
	Do not call it directly. Use the _get_cpu_info_from_cpuid function instead.
	It will safely call this function in another process.
	'''

	# Pipe all output to nothing
	sys.stdout = open(os.devnull, 'w')
	sys.stderr = open(os.devnull, 'w')

	# Get the CPU arch and bits
	arch, bits = _parse_arch(DataSource.raw_arch_string)

	# Return none if this is not an X86 CPU
	if not arch in ['X86_32', 'X86_64']:
		queue.put(_obj_to_b64({}))
		return

	# Return none if SE Linux is in enforcing mode
	cpuid = CPUID()
	if cpuid.is_selinux_enforcing:
		queue.put(_obj_to_b64({}))
		return

	# Get the cpu info from the CPUID register
	max_extension_support = cpuid.get_max_extension_support()
	cache_info = cpuid.get_cache(max_extension_support)
	info = cpuid.get_info()

	processor_brand = cpuid.get_processor_brand(max_extension_support)

	# Get the Hz and scale
	hz_actual = cpuid.get_raw_hz()
	hz_actual = _to_decimal_string(hz_actual)

	# Get the Hz and scale
	scale, hz_advertised = _get_hz_string_from_brand(processor_brand)
	info = {
	'vendor_id' : cpuid.get_vendor_id(),
	'hardware' : '',
	'brand' : processor_brand,

	'hz_advertised' : _to_friendly_hz(hz_advertised, scale),
	'hz_actual' : _to_friendly_hz(hz_actual, 0),
	'hz_advertised_raw' : _to_raw_hz(hz_advertised, scale),
	'hz_actual_raw' : _to_raw_hz(hz_actual, 0),

	'l2_cache_size' : _to_friendly_bytes(cache_info['size_kb']),
	'l2_cache_line_size' : cache_info['line_size_b'],
	'l2_cache_associativity' : hex(cache_info['associativity']),

	'stepping' : info['stepping'],
	'model' : info['model'],
	'family' : info['family'],
	'processor_type' : info['processor_type'],
	'extended_model' : info['extended_model'],
	'extended_family' : info['extended_family'],
	'flags' : cpuid.get_flags(max_extension_support)
	}

	info = {k: v for k, v in info.items() if v}
	queue.put(_obj_to_b64(info))

def _get_cpu_info_from_cpuid():
	'''
	Returns the CPU info gathered by querying the X86 cpuid register in a new process.
	Returns {} on non X86 cpus.
	Returns {} if SELinux is in enforcing mode.
	'''
	from multiprocessing import Process, Queue

	# Return {} if can't cpuid
	if not DataSource.can_cpuid:
		return {}

	# Get the CPU arch and bits
	arch, bits = _parse_arch(DataSource.raw_arch_string)

	# Return {} if this is not an X86 CPU
	if not arch in ['X86_32', 'X86_64']:
		return {}

	try:
		# Start running the function in a subprocess
		queue = Queue()
		p = Process(target=_actual_get_cpu_info_from_cpuid, args=(queue,))
		p.start()

		# Wait for the process to end, while it is still alive
		while p.is_alive():
			p.join(0)

		# Return {} if it failed
		if p.exitcode != 0:
			return {}

		# Return the result, only if there is something to read
		if not queue.empty():
			output = queue.get()
			return _b64_to_obj(output)
	except:
		pass

	# Return {} if everything failed
	return {}

def _get_cpu_info_from_proc_cpuinfo():
	'''
	Returns the CPU info gathered from /proc/cpuinfo.
	Returns {} if /proc/cpuinfo is not found.
	'''
	try:
		# Just return {} if there is no cpuinfo
		if not DataSource.has_proc_cpuinfo():
			return {}

		returncode, output = DataSource.cat_proc_cpuinfo()
		if returncode != 0:
			return {}

		# Various fields
		vendor_id = _get_field(False, output, None, '', 'vendor_id', 'vendor id', 'vendor')
		processor_brand = _get_field(True, output, None, None, 'model name','cpu', 'processor')
		cache_size = _get_field(False, output, None, '', 'cache size')
		stepping = _get_field(False, output, int, 0, 'stepping')
		model = _get_field(False, output, int, 0, 'model')
		family = _get_field(False, output, int, 0, 'cpu family')
		hardware = _get_field(False, output, None, '', 'Hardware')
		# Flags
		flags = _get_field(False, output, None, None, 'flags', 'Features')
		if flags:
			flags = flags.split()
			flags.sort()

		# Convert from MHz string to Hz
		hz_actual = _get_field(False, output, None, '', 'cpu MHz', 'cpu speed', 'clock')
		hz_actual = hz_actual.lower().rstrip('mhz').strip()
		hz_actual = _to_decimal_string(hz_actual)

		# Convert from GHz/MHz string to Hz
		scale, hz_advertised = (0, None)
		try:
			scale, hz_advertised = _get_hz_string_from_brand(processor_brand)
		except Exception:
			pass

		info = {
		'hardware' : hardware,
		'brand' : processor_brand,

		'l3_cache_size' : _to_friendly_bytes(cache_size),
		'flags' : flags,
		'vendor_id' : vendor_id,
		'stepping' : stepping,
		'model' : model,
		'family' : family,
		}

		# Make the Hz the same for actual and advertised if missing any
		if not hz_advertised or hz_advertised == '0.0':
			hz_advertised = hz_actual
			scale = 6
		elif not hz_actual or hz_actual == '0.0':
			hz_actual = hz_advertised

		# Add the Hz if there is one
		if _to_raw_hz(hz_advertised, scale) > (0, 0):
			info['hz_advertised'] = _to_friendly_hz(hz_advertised, scale)
			info['hz_advertised_raw'] = _to_raw_hz(hz_advertised, scale)
		if _to_raw_hz(hz_actual, scale) > (0, 0):
			info['hz_actual'] = _to_friendly_hz(hz_actual, 6)
			info['hz_actual_raw'] = _to_raw_hz(hz_actual, 6)

		info = {k: v for k, v in info.items() if v}
		return info
	except:
		#raise # NOTE: To have this throw on error, uncomment this line
		return {}

def _get_cpu_info_from_cpufreq_info():
	'''
	Returns the CPU info gathered from cpufreq-info.
	Returns {} if cpufreq-info is not found.
	'''
	try:
		scale, hz_brand = 1, '0.0'

		if not DataSource.has_cpufreq_info():
			return {}

		returncode, output = DataSource.cpufreq_info()
		if returncode != 0:
			return {}

		hz_brand = output.split('current CPU frequency is')[1].split('\n')[0]
		i = hz_brand.find('Hz')
		assert(i != -1)
		hz_brand = hz_brand[0 : i+2].strip().lower()

		if hz_brand.endswith('mhz'):
			scale = 6
		elif hz_brand.endswith('ghz'):
			scale = 9
		hz_brand = hz_brand.rstrip('mhz').rstrip('ghz').strip()
		hz_brand = _to_decimal_string(hz_brand)

		info = {
			'hz_advertised' : _to_friendly_hz(hz_brand, scale),
			'hz_actual' : _to_friendly_hz(hz_brand, scale),
			'hz_advertised_raw' : _to_raw_hz(hz_brand, scale),
			'hz_actual_raw' : _to_raw_hz(hz_brand, scale),
		}

		info = {k: v for k, v in info.items() if v}
		return info
	except:
		#raise # NOTE: To have this throw on error, uncomment this line
		return {}

def _get_cpu_info_from_lscpu():
	'''
	Returns the CPU info gathered from lscpu.
	Returns {} if lscpu is not found.
	'''
	try:
		if not DataSource.has_lscpu():
			return {}

		returncode, output = DataSource.lscpu()
		if returncode != 0:
			return {}

		info = {}

		new_hz = _get_field(False, output, None, None, 'CPU max MHz', 'CPU MHz')
		if new_hz:
			new_hz = _to_decimal_string(new_hz)
			scale = 6
			info['hz_advertised'] = _to_friendly_hz(new_hz, scale)
			info['hz_actual'] = _to_friendly_hz(new_hz, scale)
			info['hz_advertised_raw'] = _to_raw_hz(new_hz, scale)
			info['hz_actual_raw'] = _to_raw_hz(new_hz, scale)

		vendor_id = _get_field(False, output, None, None, 'Vendor ID')
		if vendor_id:
			info['vendor_id'] = vendor_id

		brand = _get_field(False, output, None, None, 'Model name')
		if brand:
			info['brand'] = brand

		family = _get_field(False, output, None, None, 'CPU family')
		if family and family.isdigit():
			info['family'] = int(family)

		stepping = _get_field(False, output, None, None, 'Stepping')
		if stepping and stepping.isdigit():
			info['stepping'] = int(stepping)

		model = _get_field(False, output, None, None, 'Model')
		if model and model.isdigit():
			info['model'] = int(model)

		l1_data_cache_size = _get_field(False, output, None, None, 'L1d cache')
		if l1_data_cache_size:
			info['l1_data_cache_size'] = _to_friendly_bytes(l1_data_cache_size)

		l1_instruction_cache_size = _get_field(False, output, None, None, 'L1i cache')
		if l1_instruction_cache_size:
			info['l1_instruction_cache_size'] = _to_friendly_bytes(l1_instruction_cache_size)

		l2_cache_size = _get_field(False, output, None, None, 'L2 cache')
		if l2_cache_size:
			info['l2_cache_size'] = _to_friendly_bytes(l2_cache_size)

		l3_cache_size = _get_field(False, output, None, None, 'L3 cache')
		if l3_cache_size:
			info['l3_cache_size'] = _to_friendly_bytes(l3_cache_size)

		# Flags
		flags = _get_field(False, output, None, None, 'flags', 'Features')
		if flags:
			flags = flags.split()
			flags.sort()
			info['flags'] = flags

		info = {k: v for k, v in info.items() if v}
		return info
	except:
		#raise # NOTE: To have this throw on error, uncomment this line
		return {}

def _get_cpu_info_from_dmesg():
	'''
	Returns the CPU info gathered from dmesg.
	Returns {} if dmesg is not found or does not have the desired info.
	'''
	# Just return {} if there is no dmesg
	if not DataSource.has_dmesg():
		return {}

	# If dmesg fails return {}
	returncode, output = DataSource.dmesg_a()
	if output == None or returncode != 0:
		return {}

	return _parse_dmesg_output(output)


# https://openpowerfoundation.org/wp-content/uploads/2016/05/LoPAPR_DRAFT_v11_24March2016_cmt1.pdf
# page 767
def _get_cpu_info_from_ibm_pa_features():
	'''
	Returns the CPU info gathered from lsprop /proc/device-tree/cpus/*/ibm,pa-features
	Returns {} if lsprop is not found or ibm,pa-features does not have the desired info.
	'''
	try:
		# Just return {} if there is no lsprop
		if not DataSource.has_ibm_pa_features():
			return {}

		# If ibm,pa-features fails return {}
		returncode, output = DataSource.ibm_pa_features()
		if output == None or returncode != 0:
			return {}

		# Filter out invalid characters from output
		value = output.split("ibm,pa-features")[1].lower()
		value = [s for s in value if s in list('0123456789abcfed')]
		value = ''.join(value)

		# Get data converted to Uint32 chunks
		left = int(value[0 : 8], 16)
		right = int(value[8 : 16], 16)

		# Get the CPU flags
		flags = {
			# Byte 0
			'mmu' : _is_bit_set(left, 0),
			'fpu' : _is_bit_set(left, 1),
			'slb' : _is_bit_set(left, 2),
			'run' : _is_bit_set(left, 3),
			#'reserved' : _is_bit_set(left, 4),
			'dabr' : _is_bit_set(left, 5),
			'ne' : _is_bit_set(left, 6),
			'wtr' : _is_bit_set(left, 7),

			# Byte 1
			'mcr' : _is_bit_set(left, 8),
			'dsisr' : _is_bit_set(left, 9),
			'lp' : _is_bit_set(left, 10),
			'ri' : _is_bit_set(left, 11),
			'dabrx' : _is_bit_set(left, 12),
			'sprg3' : _is_bit_set(left, 13),
			'rislb' : _is_bit_set(left, 14),
			'pp' : _is_bit_set(left, 15),

			# Byte 2
			'vpm' : _is_bit_set(left, 16),
			'dss_2.05' : _is_bit_set(left, 17),
			#'reserved' : _is_bit_set(left, 18),
			'dar' : _is_bit_set(left, 19),
			#'reserved' : _is_bit_set(left, 20),
			'ppr' : _is_bit_set(left, 21),
			'dss_2.02' : _is_bit_set(left, 22),
			'dss_2.06' : _is_bit_set(left, 23),

			# Byte 3
			'lsd_in_dscr' : _is_bit_set(left, 24),
			'ugr_in_dscr' : _is_bit_set(left, 25),
			#'reserved' : _is_bit_set(left, 26),
			#'reserved' : _is_bit_set(left, 27),
			#'reserved' : _is_bit_set(left, 28),
			#'reserved' : _is_bit_set(left, 29),
			#'reserved' : _is_bit_set(left, 30),
			#'reserved' : _is_bit_set(left, 31),

			# Byte 4
			'sso_2.06' : _is_bit_set(right, 0),
			#'reserved' : _is_bit_set(right, 1),
			#'reserved' : _is_bit_set(right, 2),
			#'reserved' : _is_bit_set(right, 3),
			#'reserved' : _is_bit_set(right, 4),
			#'reserved' : _is_bit_set(right, 5),
			#'reserved' : _is_bit_set(right, 6),
			#'reserved' : _is_bit_set(right, 7),

			# Byte 5
			'le' : _is_bit_set(right, 8),
			'cfar' : _is_bit_set(right, 9),
			'eb' : _is_bit_set(right, 10),
			'lsq_2.07' : _is_bit_set(right, 11),
			#'reserved' : _is_bit_set(right, 12),
			#'reserved' : _is_bit_set(right, 13),
			#'reserved' : _is_bit_set(right, 14),
			#'reserved' : _is_bit_set(right, 15),

			# Byte 6
			'dss_2.07' : _is_bit_set(right, 16),
			#'reserved' : _is_bit_set(right, 17),
			#'reserved' : _is_bit_set(right, 18),
			#'reserved' : _is_bit_set(right, 19),
			#'reserved' : _is_bit_set(right, 20),
			#'reserved' : _is_bit_set(right, 21),
			#'reserved' : _is_bit_set(right, 22),
			#'reserved' : _is_bit_set(right, 23),

			# Byte 7
			#'reserved' : _is_bit_set(right, 24),
			#'reserved' : _is_bit_set(right, 25),
			#'reserved' : _is_bit_set(right, 26),
			#'reserved' : _is_bit_set(right, 27),
			#'reserved' : _is_bit_set(right, 28),
			#'reserved' : _is_bit_set(right, 29),
			#'reserved' : _is_bit_set(right, 30),
			#'reserved' : _is_bit_set(right, 31),
		}

		# Get a list of only the flags that are true
		flags = [k for k, v in flags.items() if v]
		flags.sort()

		info = {
			'flags' : flags
		}
		info = {k: v for k, v in info.items() if v}

		return info
	except:
		return {}


def _get_cpu_info_from_cat_var_run_dmesg_boot():
	'''
	Returns the CPU info gathered from /var/run/dmesg.boot.
	Returns {} if dmesg is not found or does not have the desired info.
	'''
	# Just return {} if there is no /var/run/dmesg.boot
	if not DataSource.has_var_run_dmesg_boot():
		return {}

	# If dmesg.boot fails return {}
	returncode, output = DataSource.cat_var_run_dmesg_boot()
	if output == None or returncode != 0:
		return {}

	return _parse_dmesg_output(output)


def _get_cpu_info_from_sysctl():
	'''
	Returns the CPU info gathered from sysctl.
	Returns {} if sysctl is not found.
	'''
	try:
		# Just return {} if there is no sysctl
		if not DataSource.has_sysctl():
			return {}

		# If sysctl fails return {}
		returncode, output = DataSource.sysctl_machdep_cpu_hw_cpufrequency()
		if output == None or returncode != 0:
			return {}

		# Various fields
		vendor_id = _get_field(False, output, None, None, 'machdep.cpu.vendor')
		processor_brand = _get_field(True, output, None, None, 'machdep.cpu.brand_string')
		cache_size = _get_field(False, output, None, None, 'machdep.cpu.cache.size')
		stepping = _get_field(False, output, int, 0, 'machdep.cpu.stepping')
		model = _get_field(False, output, int, 0, 'machdep.cpu.model')
		family = _get_field(False, output, int, 0, 'machdep.cpu.family')

		# Flags
		flags = _get_field(False, output, None, '', 'machdep.cpu.features').lower().split()
		flags.extend(_get_field(False, output, None, '', 'machdep.cpu.leaf7_features').lower().split())
		flags.extend(_get_field(False, output, None, '', 'machdep.cpu.extfeatures').lower().split())
		flags.sort()

		# Convert from GHz/MHz string to Hz
		scale, hz_advertised = _get_hz_string_from_brand(processor_brand)
		hz_actual = _get_field(False, output, None, None, 'hw.cpufrequency')
		hz_actual = _to_decimal_string(hz_actual)

		info = {
		'vendor_id' : vendor_id,
		'brand' : processor_brand,

		'hz_advertised' : _to_friendly_hz(hz_advertised, scale),
		'hz_actual' : _to_friendly_hz(hz_actual, 0),
		'hz_advertised_raw' : _to_raw_hz(hz_advertised, scale),
		'hz_actual_raw' : _to_raw_hz(hz_actual, 0),

		'l2_cache_size' : _to_friendly_bytes(cache_size),

		'stepping' : stepping,
		'model' : model,
		'family' : family,
		'flags' : flags
		}

		info = {k: v for k, v in info.items() if v}
		return info
	except:
		return {}


def _get_cpu_info_from_sysinfo():
	'''
	Returns the CPU info gathered from sysinfo.
	Returns {} if sysinfo is not found.
	'''
	info = _get_cpu_info_from_sysinfo_v1()
	info.update(_get_cpu_info_from_sysinfo_v2())
	return info

def _get_cpu_info_from_sysinfo_v1():
	'''
	Returns the CPU info gathered from sysinfo.
	Returns {} if sysinfo is not found.
	'''
	try:
		# Just return {} if there is no sysinfo
		if not DataSource.has_sysinfo():
			return {}

		# If sysinfo fails return {}
		returncode, output = DataSource.sysinfo_cpu()
		if output == None or returncode != 0:
			return {}

		# Various fields
		vendor_id = '' #_get_field(False, output, None, None, 'CPU #0: ')
		processor_brand = output.split('CPU #0: "')[1].split('"\n')[0]
		cache_size = '' #_get_field(False, output, None, None, 'machdep.cpu.cache.size')
		stepping = int(output.split(', stepping ')[1].split(',')[0].strip())
		model = int(output.split(', model ')[1].split(',')[0].strip())
		family = int(output.split(', family ')[1].split(',')[0].strip())

		# Flags
		flags = []
		for line in output.split('\n'):
			if line.startswith('\t\t'):
				for flag in line.strip().lower().split():
					flags.append(flag)
		flags.sort()

		# Convert from GHz/MHz string to Hz
		scale, hz_advertised = _get_hz_string_from_brand(processor_brand)
		hz_actual = hz_advertised

		info = {
		'vendor_id' : vendor_id,
		'brand' : processor_brand,

		'hz_advertised' : _to_friendly_hz(hz_advertised, scale),
		'hz_actual' : _to_friendly_hz(hz_actual, scale),
		'hz_advertised_raw' : _to_raw_hz(hz_advertised, scale),
		'hz_actual_raw' : _to_raw_hz(hz_actual, scale),

		'l2_cache_size' : _to_friendly_bytes(cache_size),

		'stepping' : stepping,
		'model' : model,
		'family' : family,
		'flags' : flags
		}

		info = {k: v for k, v in info.items() if v}
		return info
	except:
		#raise # NOTE: To have this throw on error, uncomment this line
		return {}

def _get_cpu_info_from_sysinfo_v2():
	'''
	Returns the CPU info gathered from sysinfo.
	Returns {} if sysinfo is not found.
	'''
	try:
		# Just return {} if there is no sysinfo
		if not DataSource.has_sysinfo():
			return {}

		# If sysinfo fails return {}
		returncode, output = DataSource.sysinfo_cpu()
		if output == None or returncode != 0:
			return {}

		# Various fields
		vendor_id = '' #_get_field(False, output, None, None, 'CPU #0: ')
		processor_brand = output.split('CPU #0: "')[1].split('"\n')[0]
		cache_size = '' #_get_field(False, output, None, None, 'machdep.cpu.cache.size')
		signature = output.split('Signature:')[1].split('\n')[0].strip()
		#
		stepping = int(signature.split('stepping ')[1].split(',')[0].strip())
		model = int(signature.split('model ')[1].split(',')[0].strip())
		family = int(signature.split('family ')[1].split(',')[0].strip())

		# Flags
		def get_subsection_flags(output):
			retval = []
			for line in output.split('\n')[1:]:
				if not line.startswith('                ') and not line.startswith('		'): break
				for entry in line.strip().lower().split(' '):
					retval.append(entry)
			return retval

		flags = get_subsection_flags(output.split('Features: ')[1]) + \
				get_subsection_flags(output.split('Extended Features (0x00000001): ')[1]) + \
				get_subsection_flags(output.split('Extended Features (0x80000001): ')[1])
		flags.sort()

		# Convert from GHz/MHz string to Hz
		lines = [n for n in output.split('\n') if n]
		raw_hz = lines[0].split('running at ')[1].strip().lower()
		hz_advertised = raw_hz.rstrip('mhz').rstrip('ghz').strip()
		hz_advertised = _to_decimal_string(hz_advertised)
		hz_actual = hz_advertised

		scale = 1
		if raw_hz.endswith('mhz'):
			scale = 6
		elif raw_hz.endswith('ghz'):
			scale = 9

		info = {
		'vendor_id' : vendor_id,
		'brand' : processor_brand,

		'hz_advertised' : _to_friendly_hz(hz_advertised, scale),
		'hz_actual' : _to_friendly_hz(hz_actual, scale),
		'hz_advertised_raw' : _to_raw_hz(hz_advertised, scale),
		'hz_actual_raw' : _to_raw_hz(hz_actual, scale),

		'l2_cache_size' : _to_friendly_bytes(cache_size),

		'stepping' : stepping,
		'model' : model,
		'family' : family,
		'flags' : flags
		}

		info = {k: v for k, v in info.items() if v}
		return info
	except:
		#raise # NOTE: To have this throw on error, uncomment this line
		return {}

def _get_cpu_info_from_wmic():
	'''
	Returns the CPU info gathered from WMI.
	Returns {} if not on Windows, or wmic is not installed.
	'''

	try:
		# Just return {} if not Windows or there is no wmic
		if not DataSource.is_windows or not DataSource.has_wmic():
			return {}

		returncode, output = DataSource.wmic_cpu()
		if output == None or returncode != 0:
			return {}

		# Break the list into key values pairs
		value = output.split("\n")
		value = [s.rstrip().split('=') for s in value if '=' in s]
		value = {k: v for k, v in value if v}

		# Get the advertised MHz
		processor_brand = value.get('Name')
		scale_advertised, hz_advertised = _get_hz_string_from_brand(processor_brand)

		# Get the actual MHz
		hz_actual = value.get('CurrentClockSpeed')
		scale_actual = 6
		if hz_actual:
			hz_actual = _to_decimal_string(hz_actual)

		# Get cache sizes
		l2_cache_size = value.get('L2CacheSize')
		if l2_cache_size:
			l2_cache_size = l2_cache_size + ' KB'

		l3_cache_size = value.get('L3CacheSize')
		if l3_cache_size:
			l3_cache_size = l3_cache_size + ' KB'

		# Get family, model, and stepping
		family, model, stepping = '', '', ''
		description = value.get('Description') or value.get('Caption')
		entries = description.split(' ')

		if 'Family' in entries and entries.index('Family') < len(entries)-1:
			i = entries.index('Family')
			family = int(entries[i + 1])

		if 'Model' in entries and entries.index('Model') < len(entries)-1:
			i = entries.index('Model')
			model = int(entries[i + 1])

		if 'Stepping' in entries and entries.index('Stepping') < len(entries)-1:
			i = entries.index('Stepping')
			stepping = int(entries[i + 1])

		info = {
			'vendor_id' : value.get('Manufacturer'),
			'brand' : processor_brand,

			'hz_advertised' : _to_friendly_hz(hz_advertised, scale_advertised),
			'hz_actual' : _to_friendly_hz(hz_actual, scale_actual),
			'hz_advertised_raw' : _to_raw_hz(hz_advertised, scale_advertised),
			'hz_actual_raw' : _to_raw_hz(hz_actual, scale_actual),

			'l2_cache_size' : l2_cache_size,
			'l3_cache_size' : l3_cache_size,

			'stepping' : stepping,
			'model' : model,
			'family' : family,
		}

		info = {k: v for k, v in info.items() if v}
		return info
	except:
		#raise # NOTE: To have this throw on error, uncomment this line
		return {}

def _get_cpu_info_from_registry():
	'''
	FIXME: Is missing many of the newer CPU flags like sse3
	Returns the CPU info gathered from the Windows Registry.
	Returns {} if not on Windows.
	'''
	try:
		# Just return {} if not on Windows
		if not DataSource.is_windows:
			return {}

		# Get the CPU name
		processor_brand = DataSource.winreg_processor_brand()

		# Get the CPU vendor id
		vendor_id = DataSource.winreg_vendor_id()

		# Get the CPU arch and bits
		raw_arch_string = DataSource.winreg_raw_arch_string()
		arch, bits = _parse_arch(raw_arch_string)

		# Get the actual CPU Hz
		hz_actual = DataSource.winreg_hz_actual()
		hz_actual = _to_decimal_string(hz_actual)

		# Get the advertised CPU Hz
		scale, hz_advertised = _get_hz_string_from_brand(processor_brand)

		# Get the CPU features
		feature_bits = DataSource.winreg_feature_bits()

		def is_set(bit):
			mask = 0x80000000 >> bit
			retval = mask & feature_bits > 0
			return retval

		# http://en.wikipedia.org/wiki/CPUID
		# http://unix.stackexchange.com/questions/43539/what-do-the-flags-in-proc-cpuinfo-mean
		# http://www.lohninger.com/helpcsuite/public_constants_cpuid.htm
		flags = {
			'fpu' : is_set(0), # Floating Point Unit
			'vme' : is_set(1), # V86 Mode Extensions
			'de' : is_set(2), # Debug Extensions - I/O breakpoints supported
			'pse' : is_set(3), # Page Size Extensions (4 MB pages supported)
			'tsc' : is_set(4), # Time Stamp Counter and RDTSC instruction are available
			'msr' : is_set(5), # Model Specific Registers
			'pae' : is_set(6), # Physical Address Extensions (36 bit address, 2MB pages)
			'mce' : is_set(7), # Machine Check Exception supported
			'cx8' : is_set(8), # Compare Exchange Eight Byte instruction available
			'apic' : is_set(9), # Local APIC present (multiprocessor operation support)
			'sepamd' : is_set(10), # Fast system calls (AMD only)
			'sep' : is_set(11), # Fast system calls
			'mtrr' : is_set(12), # Memory Type Range Registers
			'pge' : is_set(13), # Page Global Enable
			'mca' : is_set(14), # Machine Check Architecture
			'cmov' : is_set(15), # Conditional MOVe instructions
			'pat' : is_set(16), # Page Attribute Table
			'pse36' : is_set(17), # 36 bit Page Size Extensions
			'serial' : is_set(18), # Processor Serial Number
			'clflush' : is_set(19), # Cache Flush
			#'reserved1' : is_set(20), # reserved
			'dts' : is_set(21), # Debug Trace Store
			'acpi' : is_set(22), # ACPI support
			'mmx' : is_set(23), # MultiMedia Extensions
			'fxsr' : is_set(24), # FXSAVE and FXRSTOR instructions
			'sse' : is_set(25), # SSE instructions
			'sse2' : is_set(26), # SSE2 (WNI) instructions
			'ss' : is_set(27), # self snoop
			#'reserved2' : is_set(28), # reserved
			'tm' : is_set(29), # Automatic clock control
			'ia64' : is_set(30), # IA64 instructions
			'3dnow' : is_set(31) # 3DNow! instructions available
		}

		# Get a list of only the flags that are true
		flags = [k for k, v in flags.items() if v]
		flags.sort()

		info = {
		'vendor_id' : vendor_id,
		'brand' : processor_brand,

		'hz_advertised' : _to_friendly_hz(hz_advertised, scale),
		'hz_actual' : _to_friendly_hz(hz_actual, 6),
		'hz_advertised_raw' : _to_raw_hz(hz_advertised, scale),
		'hz_actual_raw' : _to_raw_hz(hz_actual, 6),

		'flags' : flags
		}

		info = {k: v for k, v in info.items() if v}
		return info
	except:
		return {}

def _get_cpu_info_from_kstat():
	'''
	Returns the CPU info gathered from isainfo and kstat.
	Returns {} if isainfo or kstat are not found.
	'''
	try:
		# Just return {} if there is no isainfo or kstat
		if not DataSource.has_isainfo() or not DataSource.has_kstat():
			return {}

		# If isainfo fails return {}
		returncode, flag_output = DataSource.isainfo_vb()
		if flag_output == None or returncode != 0:
			return {}

		# If kstat fails return {}
		returncode, kstat = DataSource.kstat_m_cpu_info()
		if kstat == None or returncode != 0:
			return {}

		# Various fields
		vendor_id = kstat.split('\tvendor_id ')[1].split('\n')[0].strip()
		processor_brand = kstat.split('\tbrand ')[1].split('\n')[0].strip()
		stepping = int(kstat.split('\tstepping ')[1].split('\n')[0].strip())
		model = int(kstat.split('\tmodel ')[1].split('\n')[0].strip())
		family = int(kstat.split('\tfamily ')[1].split('\n')[0].strip())

		# Flags
		flags = flag_output.strip().split('\n')[-1].strip().lower().split()
		flags.sort()

		# Convert from GHz/MHz string to Hz
		scale = 6
		hz_advertised = kstat.split('\tclock_MHz ')[1].split('\n')[0].strip()
		hz_advertised = _to_decimal_string(hz_advertised)

		# Convert from GHz/MHz string to Hz
		hz_actual = kstat.split('\tcurrent_clock_Hz ')[1].split('\n')[0].strip()
		hz_actual = _to_decimal_string(hz_actual)

		info = {
		'vendor_id' : vendor_id,
		'brand' : processor_brand,

		'hz_advertised' : _to_friendly_hz(hz_advertised, scale),
		'hz_actual' : _to_friendly_hz(hz_actual, 0),
		'hz_advertised_raw' : _to_raw_hz(hz_advertised, scale),
		'hz_actual_raw' : _to_raw_hz(hz_actual, 0),

		'stepping' : stepping,
		'model' : model,
		'family' : family,
		'flags' : flags
		}

		info = {k: v for k, v in info.items() if v}
		return info
	except:
		return {}

def _get_cpu_info_from_platform_uname():
	try:
		uname = DataSource.raw_uname_string.split(',')[0]

		family, model, stepping = (None, None, None)
		entries = uname.split(' ')

		if 'Family' in entries and entries.index('Family') < len(entries)-1:
			i = entries.index('Family')
			family = int(entries[i + 1])

		if 'Model' in entries and entries.index('Model') < len(entries)-1:
			i = entries.index('Model')
			model = int(entries[i + 1])

		if 'Stepping' in entries and entries.index('Stepping') < len(entries)-1:
			i = entries.index('Stepping')
			stepping = int(entries[i + 1])

		info = {
			'family' : family,
			'model' : model,
			'stepping' : stepping
		}
		info = {k: v for k, v in info.items() if v}
		return info
	except:
		return {}

def _get_cpu_info_internal():
	'''
	Returns the CPU info by using the best sources of information for your OS.
	Returns {} if nothing is found.
	'''

	# Get the CPU arch and bits
	arch, bits = _parse_arch(DataSource.raw_arch_string)

	friendly_maxsize = { 2**31-1: '32 bit', 2**63-1: '64 bit' }.get(sys.maxsize) or 'unknown bits'
	friendly_version = "{0}.{1}.{2}.{3}.{4}".format(*sys.version_info)
	PYTHON_VERSION = "{0} ({1})".format(friendly_version, friendly_maxsize)

	info = {
		'python_version' : PYTHON_VERSION,
		'cpuinfo_version' : CPUINFO_VERSION,
		'arch' : arch,
		'bits' : bits,
		'count' : DataSource.cpu_count,
		'raw_arch_string' : DataSource.raw_arch_string,
	}

	# Try the Windows wmic
	_copy_new_fields(info, _get_cpu_info_from_wmic())

	# Try the Windows registry
	_copy_new_fields(info, _get_cpu_info_from_registry())

	# Try /proc/cpuinfo
	_copy_new_fields(info, _get_cpu_info_from_proc_cpuinfo())

	# Try cpufreq-info
	_copy_new_fields(info, _get_cpu_info_from_cpufreq_info())

	# Try LSCPU
	_copy_new_fields(info, _get_cpu_info_from_lscpu())

	# Try sysctl
	_copy_new_fields(info, _get_cpu_info_from_sysctl())

	# Try kstat
	_copy_new_fields(info, _get_cpu_info_from_kstat())

	# Try dmesg
	_copy_new_fields(info, _get_cpu_info_from_dmesg())

	# Try /var/run/dmesg.boot
	_copy_new_fields(info, _get_cpu_info_from_cat_var_run_dmesg_boot())

	# Try lsprop ibm,pa-features
	_copy_new_fields(info, _get_cpu_info_from_ibm_pa_features())

	# Try sysinfo
	_copy_new_fields(info, _get_cpu_info_from_sysinfo())

	# Try querying the CPU cpuid register
	_copy_new_fields(info, _get_cpu_info_from_cpuid())

	# Try platform.uname
	_copy_new_fields(info, _get_cpu_info_from_platform_uname())

	return info

def get_cpu_info_json():
	'''
	Returns the CPU info by using the best sources of information for your OS.
	Returns the result in a json string
	'''

	import json

	output = None

	# If running under pyinstaller, run normally
	if getattr(sys, 'frozen', False):
		info = _get_cpu_info_internal()
		output = json.dumps(info)
		output = "{0}".format(output)
	# if not running under pyinstaller, run in another process.
	# This is done because multiprocesing has a design flaw that
	# causes non main programs to run multiple times on Windows.
	else:
		from subprocess import Popen, PIPE

		command = [sys.executable, __file__, '--json']
		p1 = Popen(command, stdout=PIPE, stderr=PIPE, stdin=PIPE)
		output = p1.communicate()[0]

		if p1.returncode != 0:
			return "{}"

		if not IS_PY2:
			output = output.decode(encoding='UTF-8')

	return output

def get_cpu_info():
	'''
	Returns the CPU info by using the best sources of information for your OS.
	Returns the result in a dict
	'''

	import json

	output = get_cpu_info_json()

	# Convert JSON to Python with non unicode strings
	output = json.loads(output, object_hook = _utf_to_str)

	return output

def main():
	from argparse import ArgumentParser
	import json

	# Parse args
	parser = ArgumentParser(description='Gets CPU info with pure Python 2 & 3')
	parser.add_argument('--json', action='store_true', help='Return the info in JSON format')
	args = parser.parse_args()

	try:
		_check_arch()
	except Exception as err:
		sys.stderr.write(str(err) + "\n")
		sys.exit(1)

	info = _get_cpu_info_internal()

	if not info:
		sys.stderr.write("Failed to find cpu info\n")
		sys.exit(1)

	if args.json:
		print(json.dumps(info))
	else:
		print('Python Version: {0}'.format(info.get('python_version', '')))
		print('Cpuinfo Version: {0}'.format(info.get('cpuinfo_version', '')))
		print('Vendor ID: {0}'.format(info.get('vendor_id', '')))
		print('Hardware Raw: {0}'.format(info.get('hardware', '')))
		print('Brand: {0}'.format(info.get('brand', '')))
		print('Hz Advertised: {0}'.format(info.get('hz_advertised', '')))
		print('Hz Actual: {0}'.format(info.get('hz_actual', '')))
		print('Hz Advertised Raw: {0}'.format(info.get('hz_advertised_raw', '')))
		print('Hz Actual Raw: {0}'.format(info.get('hz_actual_raw', '')))
		print('Arch: {0}'.format(info.get('arch', '')))
		print('Bits: {0}'.format(info.get('bits', '')))
		print('Count: {0}'.format(info.get('count', '')))

		print('Raw Arch String: {0}'.format(info.get('raw_arch_string', '')))

		print('L1 Data Cache Size: {0}'.format(info.get('l1_data_cache_size', '')))
		print('L1 Instruction Cache Size: {0}'.format(info.get('l1_instruction_cache_size', '')))
		print('L2 Cache Size: {0}'.format(info.get('l2_cache_size', '')))
		print('L2 Cache Line Size: {0}'.format(info.get('l2_cache_line_size', '')))
		print('L2 Cache Associativity: {0}'.format(info.get('l2_cache_associativity', '')))
		print('L3 Cache Size: {0}'.format(info.get('l3_cache_size', '')))
		print('Stepping: {0}'.format(info.get('stepping', '')))
		print('Model: {0}'.format(info.get('model', '')))
		print('Family: {0}'.format(info.get('family', '')))
		print('Processor Type: {0}'.format(info.get('processor_type', '')))
		print('Extended Model: {0}'.format(info.get('extended_model', '')))
		print('Extended Family: {0}'.format(info.get('extended_family', '')))
		print('Flags: {0}'.format(', '.join(info.get('flags', ''))))


if __name__ == '__main__':
	main()
else:
	_check_arch()
