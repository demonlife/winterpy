import os
from collections import defaultdict, namedtuple
import subprocess
import re

from pkg_resources import parse_version

class PkgNameInfo(namedtuple('PkgNameInfo', 'name, version, release, arch')):
  def __lt__(self, other):
    if self.name != other.name or self.arch != other.arch:
      return NotImplemented
    if self.version != other.version:
      return parse_version(self.version) < parse_version(other.version)
    return int(self.release) < int(other.release)

  def __gt__(self, other):
    # No, try the other side please.
    return NotImplemented

  @property
  def fullversion(self):
    return '%s-%s' % (self.version, self.release)

  @classmethod
  def parseFilename(cls, filename):
    return cls(*trimext(filename, 3).rsplit('-', 3))

def trimext(name, num=1):
  for i in range(num):
    name = os.path.splitext(name)[0]
  return name

def get_pkgname_with_bash(PKGBUILD):
  script = '''\
. '%s'
echo ${pkgname[*]}''' % PKGBUILD
  # Python 3.4 has 'input' arg for check_output
  p = subprocess.Popen(['bash'], stdin=subprocess.PIPE,
                       stdout=subprocess.PIPE)
  output = p.communicate(script.encode('latin1'))[0].decode('latin1')
  ret = p.wait()
  if ret != 0:
    raise subprocess.CalledProcessError(
      ret, ['bash'], output)
  return output.split()

def get_aur_pkgbuild_with_bash(name):
  script = '''\
. /usr/lib/yaourt/util.sh
. /usr/lib/yaourt/aur.sh
aur_get_pkgbuild '%s' ''' % name
  p = subprocess.Popen(['bash'], stdin=subprocess.PIPE)
  p.communicate(script.encode('latin1'))
  ret = p.wait()
  if ret != 0:
    raise subprocess.CalledProcessError(
      ret, ['bash'])

pkgfile_pat = re.compile(r'(?:^|/).+-[^-]+-\d+-(?:\w+)\.pkg\.tar\.xz$')
