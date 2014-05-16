#import sys
#import datetime
#import time
import subprocess
import os
import re


class uptime:
    timere = re.compile("^(.*-)?(\d{0,2}:)?(\d{0,2}:)?(.*)$")

    def __init__(self, core, client):
        core.addCommandHandler("uptime", self, cpriv=1, chelp="uptime.help")

    def uptime(self, bot, cli, ev):
        try:
            up = self._getUptime()
            up = bot._(ev, self, "uptime.time").format(up[0], up[1],
                                                         up[2], up[3])
        except:
            up = "\2" + bot._(ev, self, "err.nouptime") + "\2"
        x = self.memory_usage()
        rss = "\2" + str(round(int(x['rss']) / 1024, 1)) + "\2"
        peak = "\2" + str(round(int(x['peak']) / 1024, 1)) + "\2"
        threads = "\2" + str(x['reads']) + "\2"
        ss = bot._(ev, self, "uptime.mem").format(rss, peak, threads)
        cli.msg(ev.target, up + ss)

    def _getUptime(self):
        #ps -o pid,etime -p 3842
        proc = subprocess.Popen(['ps', '-o', 'pid,etime', '-p',
                        str(os.getpid())], stdout=subprocess.PIPE)
        proc.wait()
        results = proc.stdout.readlines()[1].decode()
        results = results.replace(str(os.getpid()), "").strip()
        if results.count(":") == 1:
            results = "0:" + results
        res = self.timere.match(results)
        results = []
        results.insert(0, res.group(1))
        results.insert(1, res.group(2))
        results.insert(2, res.group(3))
        results.insert(3, res.group(4))
        for i, l in enumerate(results):
            if l is None:
                results[i] = "\0020\2"
            else:
                results[i] = str(int(l.strip(":").strip("-")))
                results[i] = "\2" + results[i] + "\2"
        return results

    def memory_usage(self):
        """Memory usage of the current process in kilobytes."""
        status = None
        result = {'peak': 0, 'rss': 0, 'reads': 0}
        try:
            # This will only work on systems with a /proc file system
            # (like Linux).
            status = open('/proc/self/status')
            for line in status:
                parts = line.split()
                key = parts[0][2:-1].lower()
                if key in result:
                    result[key] = int(parts[1])
        finally:
            if status is not None:
                status.close()
        print(result)
        return result