#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#

import collections
import json
import sys
from termcolor import cprint

from natsort import natsorted
from nubia import context
from nubia import exceptions
from nubia import eventbus

class NubiaCognivalContext(context.Context):
    def __init__(self, *args, **kwargs):
        self.state = {}
        self.messages = kwargs.get('messages', None)
        self.cognival_path = kwargs.get('cognival_path', None)
        
        if self.cognival_path:
            self.cog_sources_path = self.cognival_path / 'cognitive_sources'
            self.embeddings_path = self.cognival_path / 'embeddings'
            self.resources_path = self.cognival_path / 'resources'
            self.results_path = self.cognival_path / 'embeddings'
        else:
            self.cognival_path, self.embeddings_path, \
                self.resources_path, self.resources_path = [None] * 4

        self.embedding_registry = None
        self.path2embeddings = collections.defaultdict(list)
        self._load_configuration()
        super().__init__()

    def _load_configuration(self):
        if self.resources_path:
            with open(self.resources_path / 'embedding_registry.json') as f:
                self.embedding_registry = json.load(f)
            for embedding_type_dict in self.embedding_registry.values():
                for embeddings, embedding_params in embedding_type_dict.items():
                    self.path2embeddings[embedding_params['path']].append(embeddings)
            for path, emb_list in self.path2embeddings.items():
                self.path2embeddings[path] = natsorted(emb_list)
        else:
            cprint('Error: Could not load resources path, aborting ...', 'red')
            sys.exit(1)
        
    def on_connected(self, *args, **kwargs):
        pass

    def on_cli(self, cmd, args):
        # dispatch the on connected message
        self.debug = args.debug
        self.verbose = args.verbose
        self.registry.dispatch_message(eventbus.Message.CONNECTED)

    def on_interactive(self, args):
        self.debug = args.debug
        self.verbose = args.verbose
        self.no_welcome = args.no_welcome
        if not self.no_welcome:
            cprint(self.messages.LOGO_STR, "magenta")
            cprint(self.messages.WELCOME_MESSAGE_STR, "green")
        
        ret = self._registry.find_command("connect").run_cli(args)
        if ret:
            raise exceptions.CommandError("Failed starting interactive mode")
        # dispatch the on connected message
        self.registry.dispatch_message(eventbus.Message.CONNECTED)


    def save_configuration(self):
        if self.embedding_registry:
            with open(self.resources_path / 'embedding_registry.json', 'w') as f:
                json.dump(self.embedding_registry, f, indent=4)
        else:
            raise RuntimeError("No configuration loaded, cannot save!")
