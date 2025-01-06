#!/usr/bin/env python3

"""Image Builder integration for Koji."""

import koji

from koji.tasks import BaseTaskHandler


def _arches_for_build_config(build_config):
    """Canonicalize and verify architectures from a `BuildConfig`."""

    if not build_config["arches"]:
        raise koji.BuildError(f"Missing arches for tag {build_config['name']}")

    return set(koji.canonArch(arch) for arch in build_config["arches"].split())


class ImageBuilderBuildImageTask(BaseTaskHandler):
    """TODO: Orchestration task."""

    Methods = ["imageBuilderBuild"]

    def __init__(self, task_id, method, params, session, options):
        super().__init__(task_id, method, params, session, options)

        self.logger = logging.getLogger("koji.plugin.imagebuilder")

    def handler(
        self,
        name,
        version,
        distro,
        image_type,
        req_target,
        req_arches,
        opts=None,
    ):
        """The initial build task. This task spawns one task per requested
        architecture to build on."""

        target_info = self.session.getBuildTarget(req_target, strict=True)

        if not target_info:
            raise koji.BuildError(f"Target {req_target!r} not found")

        build_config = self.session.getBuildConfig(target_info["build_tag"])

        # Get available architectures for the tag that is being built
        tag_arches = _arches_for_build_config(build_config)

        # If there are specific requested architectures then check that the
        # requested architectures are all available for the tag being built
        if req_arches:
            for arch in req_arches:
                if koji.canonArch(arch) not in tag_arches:
                    raise koji.BuildError(
                        "Invalid arch for build tag: %s" % arch
                    )
        else:
            # Otherwise build all available architectures
            req_arches = tag_arches

        # TODO: Repositories

        # TODO: Version and Names

        """
        if opts is None:
            opts = {}

        if not opts.get("scratch"):
            opts["scratch"] = False

        if not opts.get("optional_arches"):
            opts["optional_arches"] = []

        if not build_config["extra"].get("mock.new_chroot", True):
            opts["mount_dev"] = True

        self.opts = opts

        # XXX set default name, version, and default_profile
        name = ""
        version = ""

        build_info = {}

        if opts.get("version"):
            version = version

        if opts.get("release"):
            release = opts["release"]
        else:
            release = self.session.getNextRelease(
                {"name": name, "version": version}
            )

        if not opts["scratch"]:
            build_info = self.initImageBuild(  # where does this come from?
                name,
                version,
                release,
                target_info,
                self.opts,
            )

            release = build_info["release"]
        else:
            build_info = {}
        """


class ImageBuilderCreateImageTask(BaseBuildTask):
    """TODO: Runs on the actual machine that does the build."""

    Methods = ["createImageBuilderImage"]

    def handler(
        self,
        name,
        version,
        release,
        arch,
        target_info,
        build_tag,
        repo_info,
        desc_url,
        desc_path,
        opts=None,
    ):
        # XXX, do we need the BuildRoot?
        root = BuildRoot(
            self.session,
            self.options,
            tag=build_tag,
            task_id=self.id,
            repo_id=None,  # XXX,
            install_group="kiwi-build",  # XXX
            setup_dns=True,
            bind_opts=None,  # XXX
        )
        root.workdir = self.workdir
