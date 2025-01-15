lookup = {'cz': 'Czechia', 'de': 'Germany',
          'fi': 'Finland'}
filtered = [(x, lookup[x]) for x
            in ['ab', 'bc', 'cd', 'de', 'ef']
            if x in lookup]
print(filtered)