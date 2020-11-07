def from_decay_chain(decay):
    if isinstance(decay, str):
        return decay  # TODO: create particle

    decay = decay.copy()
    if isinstance(decay, dict):
        _ = decay.pop('model')
        _ = decay.pop('model_params')
        zfit_info = decay.pop("zfit", None)
        particle_name, children_decay = decay.popitem()
        assert not decay, "Items left that were not supposed to be in there"
        # TODO: create particle
        particle = particle_name
        branches = [from_decay_chain_branch(children_dec) for children_dec in children_decay]

        particle_branches = []
        for branch in branches:
            # TODO: copy particle, set children
            particle_branches.append(particle + branch)

    elif isinstance(decay, list):
        children = [from_decay_chain(dec) for dec in decay]

    else:
        raise ValueError("Currently, only str, list and dict are accepted")


def from_decay_chain_branch(decay):
    fracs = []
    children = []
    for branch in decay:
        fracs.append(branch['bf'])
        children = from_decay_chain(from_decay_chain(branch['fs']))
    return children


if __name__ == '__main__':
    decay = {'B0': [{'bf': 4.33e-05,
                     'fs': [
                         {'K*0': [{'bf': 0.6657,
                                   'fs': ['K+', 'pi-'],
                                   'model': 'VSS',
                                   'model_params': '',
                                   'zfit': {'model': 'rel-BW', 'params': []}}]},
                         'gamma'
                     ],
                     'model': 'HELAMP',
                     'model_params': [1.0, 0.0, 1.0, 0.0]}]
             }

    import decaylanguage as dl

    dm1 = dl.DecayMode(0.000043300, 'K*0 gamma', model='HELAMP', model_params=[1.0, 0.0, 1.0, 0.0])
    dm2 = dl.DecayMode(0.6657, 'K+ pi-', model='VSS', zfit={'model': 'rel-BW', 'params': []})
    dc = dl.DecayChain('B0', {'B0': dm1, 'K*0': dm2})
    dc.to_dict()
