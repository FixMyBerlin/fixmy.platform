from django.contrib.gis.gdal import OGRGeometry
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
import django.contrib.gis.utils
import sys
import pytz


class LayerMapping(django.contrib.gis.utils.LayerMapping):
    def save(
        self,
        verbose=False,
        fid_range=False,
        step=False,
        progress=False,
        silent=False,
        stream=sys.stdout,
        strict=False,
    ):
        """
        Create or update model instances, updating their geometries as well.
        Timezone unaware datetime fields are converted to timezone aware 
        values by assuming they are in UTC.
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
                        stream.write('Ignoring feature id: {}\n'.format(feat.fid, msg))
                else:
                    # Always create timezone aware datetime values
                    # and assume UTC for unaware datetime objects
                    for k in kwargs.keys():
                        if type(kwargs[k]) == datetime and kwargs[k].tzinfo is None:
                            kwargs[k] = kwargs[k].replace(tzinfo=pytz.UTC)

                    if self.unique:
                        is_update = True
                        try:
                            # Constructing the model using the keyword args
                            # If we want unique models on a particular field, handle the
                            # geometry appropriately.
                            # Getting the keyword arguments and retrieving
                            # the unique model.
                            u_kwargs = self.unique_kwargs(kwargs)
                            m = self.model.objects.using(self.using).get(**u_kwargs)

                            # Replace the geometry with the geometry from the
                            # shape file
                            new = OGRGeometry(kwargs[self.geom_field])
                            setattr(m, self.geom_field, new.wkt)

                            # Update existing model fields
                            for k, v in kwargs.items():
                                if k == self.geom_field:
                                    continue

                                setattr(m, k, v)
                        except ObjectDoesNotExist:
                            # No unique model exists yet, create.
                            is_update = False
                            m = self.model(**kwargs)
                    else:
                        is_update = False
                        m = self.model(**kwargs)

                    try:
                        # Attempting to save.
                        m.save(using=self.using)
                        num_saved += 1
                        if verbose:
                            stream.write(
                                '%s: %s\n' % ('Updated' if is_update else 'Saved', m)
                            )
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
                            stream.write(
                                'Failed to save %s:\n %s\nContinuing\n' % (kwargs, msg)
                            )

                # Printing progress information, if requested.
                if progress and num_feat % progress_interval == 0:
                    stream.write(
                        'Processed %d features, saved %d ...\n' % (num_feat, num_saved)
                    )

            # Only used for status output purposes -- incremental saving uses the
            # values returned here.
            return num_saved, num_feat

        if self.transaction_decorator is not None:
            _save = self.transaction_decorator(_save)

        nfeat = self.layer.num_feat
        if step and isinstance(step, int) and step < nfeat:
            # Incremental saving is requested at the given interval (step)
            if default_range:
                raise django.contrib.gis.utils.LayerMapError(
                    'The `step` keyword may not be used in conjunction with the `fid_range` keyword.'
                )
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
                    stream.write(
                        '%s\nFailed to save slice: %s\n' % ('=-' * 20, step_slice)
                    )
                    raise
        else:
            # Otherwise, just calling the previously defined _save() function.
            _save()
