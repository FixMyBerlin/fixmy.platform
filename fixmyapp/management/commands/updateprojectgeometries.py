from django.contrib.gis.gdal import OGRGeometry
from django.core.management.base import BaseCommand
from fixmyapp.models import Project
import django.contrib.gis.utils
import os
import sys


class LayerMapping(django.contrib.gis.utils.LayerMapping):
    def save(self, verbose=False, fid_range=False, step=False,
             progress=False, silent=False, stream=sys.stdout, strict=False):
        """
        Updates the geometries of the instances identified by the unique key,
        replacing existing geometries. The parent class' save method adds
        geometries instead of replacing them.
        """
        # Getting the default Feature ID range.
        default_range = self.check_fid_range(fid_range)

        # Setting the progress interval, if requested.
        if progress:
            if progress is True or not isinstance(progress, int):
                progress_interval = 1000
            else:
                progress_interval = progress

        def _save(feat_range=default_range, num_feat=0, num_saved=0):
            if feat_range:
                layer_iter = self.layer[feat_range]
            else:
                layer_iter = self.layer

            for feat in layer_iter:
                num_feat += 1
                # Getting the keyword arguments
                try:
                    kwargs = self.feature_kwargs(feat)
                except django.contrib.gis.utils.LayerMapError as msg:
                    # Something borked the validation
                    if strict:
                        raise
                    elif not silent:
                        stream.write('Ignoring Feature ID %s because: %s\n' % (feat.fid, msg))
                else:
                    # Constructing the model using the keyword args
                    # If we want unique models on a particular field, handle the
                    # geometry appropriately.
                    # Getting the keyword arguments and retrieving
                    # the unique model.
                    u_kwargs = self.unique_kwargs(kwargs)
                    m = self.model.objects.using(self.using).get(**u_kwargs)
                    is_update = True

                    # Replace the geometry with the geometry from the
                    # shape file
                    new = OGRGeometry(kwargs[self.geom_field])
                    setattr(m, self.geom_field, new.wkt)

                    try:
                        # Attempting to save.
                        m.save(using=self.using)
                        num_saved += 1
                        if verbose:
                            stream.write('%s: %s\n' % ('Updated' if is_update else 'Saved', m))
                    except Exception as msg:
                        if strict:
                            # Bailing out if the `strict` keyword is set.
                            if not silent:
                                stream.write(
                                    'Failed to save the feature (id: %s) into the '
                                    'model with the keyword arguments:\n' % feat.fid
                                )
                                stream.write('%s\n' % kwargs)
                            raise
                        elif not silent:
                            stream.write('Failed to save %s:\n %s\nContinuing\n' % (kwargs, msg))

                # Printing progress information, if requested.
                if progress and num_feat % progress_interval == 0:
                    stream.write('Processed %d features, saved %d ...\n' % (num_feat, num_saved))

            # Only used for status output purposes -- incremental saving uses the
            # values returned here.
            return num_saved, num_feat

        if self.transaction_decorator is not None:
            _save = self.transaction_decorator(_save)

        nfeat = self.layer.num_feat
        if step and isinstance(step, int) and step < nfeat:
            # Incremental saving is requested at the given interval (step)
            if default_range:
                raise django.contrib.gis.utils.LayerMapError('The `step` keyword may not be used in conjunction with the `fid_range` keyword.')
            beg, num_feat, num_saved = (0, 0, 0)
            indices = range(step, nfeat, step)
            n_i = len(indices)

            for i, end in enumerate(indices):
                # Constructing the slice to use for this step; the last slice is
                # special (e.g, [100:] instead of [90:100]).
                if i + 1 == n_i:
                    step_slice = slice(beg, None)
                else:
                    step_slice = slice(beg, end)

                try:
                    num_feat, num_saved = _save(step_slice, num_feat, num_saved)
                    beg = end
                except Exception:  # Deliberately catch everything
                    stream.write('%s\nFailed to save slice: %s\n' % ('=-' * 20, step_slice))
                    raise
        else:
            # Otherwise, just calling the previously defined _save() function.
            _save()


class Command(BaseCommand):
    help = 'Update project geometries'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help='A shape file')
        parser.add_argument(
            'type',
            choices=['multipoint', 'linestring'],
            help='The type of geometries in the shape file'
        )
        parser.add_argument(
            '--show-progress',
            action='store_true',
            dest='progress',
            help='display the progress bar in any verbosity level.'
        )

    def handle(self, *args, **options):
        mapping = {
            'project_key': 'ProjectKey',
            'geometry': options['type'],
        }
        lm = LayerMapping(
            Project,
            os.path.abspath(options['file']),
            mapping,
            transform=True,
            encoding='utf-8',
            unique=('project_key',)
        )
        lm.save(
            verbose=True if options['verbosity'] > 2 else False,
            progress=options['progress'] or options['verbosity'] > 1,
            silent=options['verbosity'] == 0,
            stream=self.stdout,
            strict=True
        )
