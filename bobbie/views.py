"""
views: different ways to view a chrisjen project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2022, Corey Rayburn Yung
License: Apache-2.0

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

Contents:
    Outline
    Workflow
    Summary
    Results

To Do:

        
"""
from __future__ import annotations
import abc
from collections.abc import (
    Hashable, Mapping, MutableMapping, MutableSequence, Set)
import dataclasses
import itertools
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Type

import camina
import holden

from ..core import framework
from ..core import keystones
from ..core import nodes


@dataclasses.dataclass
class Outline(keystones.View):
    """Provides a different view of data stored in 'project.idea'.
    
    The properties in Outline are used in the construction of a Workflow. So,
    even if you do not have any interest in using its view of the configuration
    settings, it shouldn't be cut out of a Project (unless you also replace the
    functions for creating a Workflow). 

    Args:
        name
        project (framework.Project): a related project instance which has data
            from which the properties of an Outline can be derived.

    """
    name: Optional[str] = None
    project: Optional[framework.Project] = dataclasses.field(
        default = None, repr = False, compare = False)
    rules: Optional[dict[str, tuple[str]]] = dataclasses.field(
        default_factory = lambda: framework.Rules.parsers)
    
    """ Properties """       
                     
    @property
    def associations(self) -> dict[str, str]:
        """Returns associated parent of nodes in a chrisjen project.

        Returns:
            dict[str, str]: keys are node names and values are associated worker 
                names for the key nodes.
            
        """
        associations = {}
        for node, connections in self.connections.items():
            new_associations = {c: node for c in connections}
            associations.update(new_associations)
        return associations
   
    @property
    def connections(self) -> dict[str, list[str]]:
        """Returns raw connections between nodes from 'project'.
        
        Returns:
            dict[str, dict[str, list[str]]]: keys are worker names and values 
                node connections for that worker.
            
        """
        suffixes = self.plurals
        connections = {}
        for name, section in self.workers.items():
            if name.startswith(self.project.name):
                label = self.project.name
            else:
                label = name  
            worker_keys = [k for k in section.keys() if k.endswith(suffixes)]
            for key in worker_keys:
                prefix, suffix = camina.cleave_str(key)
                values = camina.listify(section[key])
                if prefix == suffix:
                    if label in connections:
                        connections[label].extend(values)
                    else:
                        connections[label] = values
                else:
                    if prefix in connections:
                        connections[prefix].extend(values)
                    else:
                        connections[prefix] = values
        return connections
                     
    @property
    def designs(self) -> dict[str, str]:
        """Returns designs of nodes in a chrisjen project.

        Returns:
            dict[str, str]: keys are node names and values are design names.
            
        """
        designs = {}
        for key, section in self.workers.items():
            design_keys = [
                k for k in section.keys() 
                if k.endswith(self.rules['design'])]
            for design_key in design_keys:
                prefix, suffix = camina.cleave_str(design_key)
                if prefix == suffix:
                    designs[key] = section[design_key]
                else:
                    designs[prefix] = section[design_key]
        return designs
                            
    @property
    def files(self) -> dict[str, Any]:
        """Returns file settings in a chrisjen project.

        Returns:
            dict[str, Any]: dict of file settings.
            
        """
        for name in self.rules['files']:
            try:
                return self[name]
            except KeyError:
                pass
        return {} 
                            
    @property
    def manager(self) -> dict[str, Any]:
        """Returns manager settings of a chrisjen project.

        Returns:
            dict[str, Any]: manager settings for a chrisjen project
            
        """
        for name, section in self.project.idea.items():
            if name.endswith(self.rules['manager']):
                return section
        for name, section in self.project.idea.items():
            suffixes = itertools.chain_from_iterable(self.rules.values()) 
            if not name.endswith(suffixes):
                return section
        return {}
     
    @property
    def general(self) -> dict[str, Any]:
        """Returns general settings in a chrisjen project.

        Returns:
            dict[str, Any]: dict of general settings.
            
        """       
        for name in self.rules['general']:
            try:
                return self[name]
            except KeyError:
                pass
        return {}  
                                    
    @property
    def implementation(self) -> dict[str, dict[str, Any]]:
        """Returns implementation parameters for nodes.
        
        These values will be parsed into arguments and attributes once the nodes
        are instanced.

        Returns:
            dict[str, dict[str, Any]]: keys are node names and values are dicts
                of the implementation arguments and attributes.
            
        """
        implementation = {}      
        for name, section in self.project.idea.items():
            for suffix in self.rules['parameters']:
                if name.endswith(suffix):
                    key = name.removesuffix('_' + suffix)
                    implementation[key] = section
        return implementation
                                                             
    @property
    def initialization(self) -> dict[str, dict[str, Any]]:
        """Returns initialization arguments and attributes for nodes.
        
        These values will be parsed into arguments and attributes once the nodes
        are instanced. They are derived from 'settings'.

        Returns:
            dict[str, dict[str, Any]]: keys are node names and values are dicts
                of the initialization arguments and attributes.
            
        """
        initialization = {}
        all_plurals = (
            self.plurals
            + self.rules['design']
            + self.rules['manager'])
        for key, section in self.workers.items():   
            initialization[key] = {
                k: v for k, v in section.items() if not k.endswith(all_plurals)}
        return initialization
        
    @property
    def kinds(self) -> dict[str, str]:
        """Returns kinds of nodes in 'project'.

        Returns:
            dict[str, str]: keys are names of nodes and values are names of the
                associated base kind types.
            
        """
        kinds = {}
        suffixes = self.plurals
        for key, section in self.workers.items():
            new_kinds = {}
            keys = [k for k in section.keys() if k.endswith(suffixes)]
            for key in keys:
                _, suffix = camina.cleave_str(key)
                values = list(camina.iterify(section[key]))
                if values not in [['none'], ['None'], ['NONE']]:
                    if suffix.endswith('s'):
                        kind = suffix[:-1]
                    else:
                        kind = suffix            
                    new_kinds.update(dict.fromkeys(values, kind))
            kinds.update(new_kinds)  
        return kinds
    
    @property
    def labels(self) -> list[str]:
        """Returns names of nodes in 'project'.

        Returns:
            list[str]: names of all nodes that are listed in 'prsettings'.
            
        """
        labels = []    
        for key, values in self.connections.items():
            labels.append(key)
            labels.extend(values)
        return camina.deduplicate_list(item = labels)    

    @property
    def plurals(self) -> tuple[str]:
        """Returns all node names as naive plurals of those names.
        
        Returns:
            tuple[str]: all node names with an 's' added in order to create 
                simple plurals combined with the stored keys.
                
        """
        plurals = [k + 's' for k in self.project.library.node.keys()]
        return tuple(plurals ) 
    
    @property
    def workers(self) -> dict[str, dict[str, Any]]:
        """Returns worker-related sections of chrisjen project settings.
        
        Any section that does not have a special suffix in 'suffixes' is deemed
        to be a worker-related section.

        Returns:
            dict[str, dict[str, Any]]: workers-related sections of settings.
            
        """
        sections = {}
        suffixes = self.plurals
        for name, section in self.project.idea.items():
            if any(k.endswith(suffixes) for k in section.keys()):
                if name.endswith('_project'):
                    name = name[:-8]
                sections[name] = section
        return sections
    

@dataclasses.dataclass
class Workflow(keystones.View):
    """Provides a different view of data stored in 'project.idea'.

    Args:
        project (framework.Project): a related project instance which has data
            from which the properties of an Outline can be derived.

    """
    name: Optional[str] = None
    project: Optional[framework.Project] = dataclasses.field(
        default = None, repr = False, compare = False)

    """ Required Subclass Property """
    
    @abc.abstractproperty
    def graph(self) -> holden.System:
        """Returns direct graph of the project workflow.

        Returns:
            holden.System: direct graph of the project workflow.
        """        
        pass
    
    """ Properties """
          
    @property
    def connections(self) -> list[str]:
        """Returns raw connections between nodes from 'project'.
        
        Returns:
            list[str]: names of top-level nodes in the project workflow.
            
        """
        suffixes = self.project.outline.plurals
        section = self.project.outline.manager
        keys = [k for k in section.keys() if k.endswith(suffixes)]
        connects = []
        for key in keys:
            new_connects = camina.iterify(section[key])
            connects.extend(new_connects)
        return connects
        
    @property
    def design(self) -> str:
        """Returns a str name of the workflow design.

        Returns:
            str: name of workflow design.
            
        """
        
        try:
            return self.project.outline.designs[self.project.name]
        except KeyError:
            return self.project.rules.default_workflow
        
    """ Public Methods """
    
    @classmethod
    def create(
        cls, 
        project: framework.Project,
        name: Optional[str] = None,
        **kwargs: Any) -> Workflow:
        """[summary]

        Args:
            project (framework.Project): [description]

        Returns:
            Workflow: [description]
            
        """ 
        name = name or project.name
        try:
            subclass = project.library.view[name]
        except KeyError:
            design = project.outline.designs[name]
            subclass = project.library.view[design]
        return subclass(name, project)  

    # def append_depth(
    #     self, 
    #     item: MutableMapping[Hashable, MutableSequence[Hashable]]) -> None:
    #     """[summary]

    #     Args:
    #         item (MutableMapping[Hashable, MutableSequence[Hashable]]): 
    #             [description]

    #     Returns:
    #         [type]: [description]
            
    #     """        
    #     first_key = list(item.keys())[0]
    #     self.append(first_key)
    #     for node in item[first_key]:
    #         self.append(item[node])
    #     return self   
    
    # def append_product(
    #     self, 
    #     item: MutableMapping[Hashable, MutableSequence[Hashable]]) -> None:
    #     """[summary]

    #     Args:
    #         item (MutableMapping[Hashable, MutableSequence[Hashable]]): 
    #             [description]

    #     Returns:
    #         [type]: [description]
            
    #     """        
    #     first_key = list(item.keys())[0]
    #     self.append(first_key)
    #     possible = [v for k, v in item.items() if k in item[first_key]]
    #     combos = list(itertools.product(*possible))
    #     self.append(combos)
    #     return self
        
    # """ Dunder Methods """
    
    # def __getattr__(self, item: str) -> Any:
    #     """Checks 'worker' for attribute named 'item'.

    #     Args:
    #         item (str): name of attribute to check.

    #     Returns:
    #         Any: contents of worker attribute named 'item'.
            
    #     """
    #     try:
    #         return object.__getattribute__(self.worker, item)
    #     except AttributeError:
    #         return AttributeError(
    #             f'{item} is not in the workflow or its primary worker')

 
# @dataclasses.dataclass
# class Summary(camina.Dictionary):
#     """Reports from completion of a chrisjen project.
    
#     Args:
#         contents (MutableMapping[Hashable, Any]): stored dictionary. Defaults 
#             to an empty dict.
#         default_factory (Optional[Any]): default value to return or default 
                          
#     """
#     contents: MutableMapping[Hashable, Any] = dataclasses.field(
#         default_factory = dict)
#     default_factory: Optional[Any] = None
    
#     """ Public Methods """

#     @classmethod
#     def create(cls, project: framework.Project) -> Summary:
#         """[summary]

#         Args:
#             project (framework.Project): [description]

#         Returns:
#             Results: [description]
            
#         """        
#         return workshop.represent_results(project = project, base = cls)

#     # def complete(
#     #     self, 
#     #     project: framework.Project, 
#     #     **kwargs) -> framework.Project:
#     #     """Calls the 'implement' method the number of times in 'iterations'.

#     #     Args:
#     #         project (framework.Project): instance from which data needed for 
#     #             implementation should be derived and all results be added.

#     #     Returns:
#     #         framework.Project: with possible changes made.
            
#     #     """
#     #     if self.contents not in [None, 'None', 'none']:
#     #         for node in self:
#     #             project = node.complete(project = project, **kwargs)
#     #     return project
    
      
# """ Public Functions """
