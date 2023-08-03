class FilterModule(object):
    def filters(self):
        return {
            'select_by_user': self.select_by_user,
        }

    def select_by_user(self, users, inv_hostname, group_names):
        d = {}

        for user in users:
            username = user['username']

            if inv_hostname in user['servers']:
                d[username] = True
                continue

            found = False

            for server in user['servers']:
                if server not in group_names:
                    continue

                found = True
                break

            d[username] = found

        return d
