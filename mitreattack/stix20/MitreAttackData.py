""" MitreAttackData Library """

from itertools import chain
from stix2 import MemoryStore, Filter
from stix2.utils import get_type_from_id
from mitreattack.stix20.custom_attack_objects import StixObjectFactory, Matrix, Tactic, DataSource, DataComponent

class MitreAttackData:
    """ MitreAttackData object """

    stix_types = [
        'attack-pattern',
        'malware',
        'tool',
        'intrusion-set',
        'campaign',
        'course-of-action',
        'x-mitre-matrix',
        'x-mitre-tactic',
        'x-mitre-data-source',
        'x-mitre-data-component'
    ]

    def __init__(self, stix_filepath: str):
        """Initialize a MitreAttackData object.

        Parameters
        ----------
        stix_file : str
            Filepath to a STIX 2.0 bundle
        """
        if not isinstance(stix_filepath, str):
            raise TypeError(f"Argument stix_filepath must be of type str, not {type(stix_filepath)}")

        self.src = MemoryStore()
        self.src.load_from_file(stix_filepath)

    ###################################
    # STIX Objects Section
    ###################################

    def remove_revoked_deprecated(self, stix_objects: list) -> list:
        """Remove revoked or deprecated objects from queries made to the data source.

        Parameters
        ----------
        stix_objects : list
            list of STIX objects from a query made to the data source

        Returns
        -------
        list
            list of STIX objects with revoked and deprecated objects filtered out
        """
        # Note we use .get() because the property may not be present in the JSON data. The default is False
        # if the property is not set.
        return list(
            filter(
                lambda x: x.get('x_mitre_deprecated', False) is False and x.get('revoked', False) is False,
                stix_objects
            )
        )

    def get_matrices(self, remove_revoked_deprecated=False) -> list:
        """Retrieve all matrix objects.

        Parameters
        ----------
        remove_revoked_deprecated : bool, optional
            remove revoked or deprecated objects from the query, by default False

        Returns
        -------
        list
            a list of Matrix objects
        """
        matrices = self.src.query([ Filter('type', '=', 'x-mitre-matrix') ])
        if remove_revoked_deprecated:
            matrices = self.remove_revoked_deprecated(matrices)
        # since Matrix is a custom object, we need to reconstruct the query results
        return [Matrix(**m, allow_custom=True) for m in matrices]

    def get_tactics(self, remove_revoked_deprecated=False) -> list:
        """Retrieve all tactic objects.

        Parameters
        ----------
        remove_revoked_deprecated : bool, optional
            remove revoked or deprecated objects from the query, by default False

        Returns
        -------
        list
            a list of Tactic objects
        """
        tactics = self.src.query([ Filter('type', '=', 'x-mitre-tactic') ])
        if remove_revoked_deprecated:
            tactics = self.remove_revoked_deprecated(tactics)
        # since Tactic is a custom object, we need to reconstruct the query results
        return [Tactic(**t, allow_custom=True) for t in tactics]

    def get_techniques(self, remove_revoked_deprecated=False) -> list:
        """Retrieve all technique objects.

        Parameters
        ----------
        remove_revoked_deprecated : bool, optional
            remove revoked or deprecated objects from the query, by default False

        Returns
        -------
        list
            a list of AttackPattern objects
        """
        techniques = self.src.query([ Filter('type', '=', 'attack-pattern') ])
        if remove_revoked_deprecated:
            techniques = self.remove_revoked_deprecated(techniques)
        return techniques

    def get_mitigations(self, remove_revoked_deprecated=False) -> list:
        """Retrieve all mitigation objects.

        Parameters
        ----------
        remove_revoked_deprecated : bool, optional
            remove revoked or deprecated objects from the query, by default False

        Returns
        -------
        list
            a list of CourseOfAction objects
        """
        mitigations = self.src.query([ Filter('type', '=', 'course-of-action') ])
        if remove_revoked_deprecated:
            mitigations = self.remove_revoked_deprecated(mitigations)
        return mitigations
    
    def get_groups(self, remove_revoked_deprecated=False) -> list:
        """Retrieve all group objects.

        Parameters
        ----------
        remove_revoked_deprecated : bool, optional
            remove revoked or deprecated objects from the query, by default False

        Returns
        -------
        list
            a list of IntrusionSet objects
        """
        groups = self.src.query([ Filter('type', '=', 'intrusion-set') ])
        if remove_revoked_deprecated:
            groups = self.remove_revoked_deprecated(groups)
        return groups

    def get_software(self, remove_revoked_deprecated=False) -> list:
        """Retrieve all software objects.

        Parameters
        ----------
        remove_revoked_deprecated : bool, optional
            remove revoked or deprecated objects from the query, by default False

        Returns
        -------
        list
            a list of Tool and Malware objects
        """
        software = list(chain.from_iterable(
            self.src.query(f) for f in [
                Filter('type', '=', 'tool'), 
                Filter('type', '=', 'malware')
            ]
        ))
        if remove_revoked_deprecated:
            software = self.remove_revoked_deprecated(software)
        return software
    
    def get_campaigns(self, remove_revoked_deprecated=False) -> list:
        """Retrieve all campaign objects.

        Parameters
        ----------
        remove_revoked_deprecated : bool, optional
            remove revoked or deprecated objects from the query, by default False

        Returns
        -------
        list
            a list of Campaign objects
        """
        campaigns = self.src.query([ Filter('type', '=', 'campaign') ])
        if remove_revoked_deprecated:
            campaigns = self.remove_revoked_deprecated(campaigns)
        return campaigns

    def get_datasources(self, remove_revoked_deprecated=False) -> list:
        """Retrieve all data source objects.

        Parameters
        ----------
        remove_revoked_deprecated : bool, optional
            remove revoked or deprecated objects from the query, by default False

        Returns
        -------
        list
            a list of DataSource objects
        """
        datasources = self.src.query([ Filter('type', '=', 'x-mitre-data-source') ])
        if remove_revoked_deprecated:
            datasources = self.remove_revoked_deprecated(datasources)
        # since DataSource is a custom object, we need to reconstruct the query results
        return [DataSource(**ds, allow_custom=True) for ds in datasources]

    def get_datacomponents(self, remove_revoked_deprecated=False) -> list:
        """Retrieve all data component objects.

        Parameters
        ----------
        remove_revoked_deprecated : bool, optional
            remove revoked or deprecated objects from the query, by default False

        Returns
        -------
        list
            a list of DataComponent objects
        """
        datacomponents = self.src.query([ Filter('type', '=', 'x-mitre-data-component') ])
        if remove_revoked_deprecated:
            datacomponents = self.remove_revoked_deprecated(datacomponents)
        # since DataComponent is a custom object, we need to reconstruct the query results
        return [DataComponent(**dc, allow_custom=True) for dc in datacomponents]

    ###################################
    # Get STIX Objects by Value
    ###################################

    def get_objects_by_content(self, content: str, object_type: str=None, remove_revoked_deprecated=False) -> list:
        """Retrieve objects by the content of their description.

        Parameters
        ----------
        content : str
            the content string to search for
        object_type : str, optional
            the STIX object type (must be 'attack-pattern', 'malware', 'tool', 'intrusion-set',
            'campaign', 'course-of-action', 'x-mitre-matrix', 'x-mitre-tactic',
            'x-mitre-data-source', or 'x-mitre-data-component')
        remove_revoked_deprecated : bool, optional
            remove revoked or deprecated objects from the query, by default False

        Returns
        -------
        list
            a list of objects where the given content string appears in the description
        """
        objects = self.src
        if object_type:
            if object_type not in self.stix_types:
                # invalid object type
                raise ValueError(f"object_type must be one of {self.stix_types}")
            else:
                # filter for objects of given type
                objects = self.src.query([ Filter('type', '=', object_type) ])

        objects = list(filter(lambda t: content.lower() in t.description.lower(), objects))
        if remove_revoked_deprecated:
            objects = self.remove_revoked_deprecated(objects)
        return objects

    def get_techniques_by_platform(self, platform: str, remove_revoked_deprecated=False) -> list:
        """Retrieve techniques under a specific platform.

        Parameters
        ----------
        platform : str
            platform to search
        remove_revoked_deprecated : bool, optional
            remove revoked or deprecated objects from the query, by default False

        Returns
        -------
        list
            a list of AttackPattern objects under the given platform
        """
        filter = [
            Filter('type', '=', 'attack-pattern'),
            Filter('x_mitre_platforms', 'contains', platform)
        ]
        techniques = self.src.query(filter)
        if remove_revoked_deprecated:
            techniques = self.remove_revoked_deprecated(techniques)
        return techniques

    def get_techniques_by_tactic(self, tactic_shortname: str, domain: str, remove_revoked_deprecated=False) -> list:
        """Retrieve techniques by tactic.

        Parameters
        ----------
        tactic_shortname : str
            the x_mitre_shortname of the tactic (e.g. 'defense-evasion')
        domain : str
            domain of the tactic (must be 'enterprise-attack', 'mobile-attack', or 'ics-attack')
        remove_revoked_deprecated : bool, optional
            remove revoked or deprecated objects from the query, by default False

        Returns
        -------
        list
            a list of AttackPattern objects under the given tactic
        """
        # validate domain input
        domain_to_kill_chain = {
            "enterprise-attack": "mitre-attack",
            "mobile-attack": "mitre-mobile-attack",
            "ics-attack": "mitre-ics-attack"
        }
        if domain not in domain_to_kill_chain.keys():
            raise ValueError(f"domain must be one of {domain_to_kill_chain.keys()}")

        # query techniques by tactic/domain; kill_chain_name differs by domain
        techniques = self.src.query([
            Filter('type', '=', 'attack-pattern'),
            Filter('kill_chain_phases.phase_name', '=', tactic_shortname),
            Filter('kill_chain_phases.kill_chain_name', '=', domain_to_kill_chain[domain]),
        ])
        if remove_revoked_deprecated:
            techniques = self.remove_revoked_deprecated(techniques)
        return techniques

    def get_tactics_by_matrix(self) -> dict:
        """Retrieve the structured list of tactics within each matrix. The order of the tactics in
        the list matches the ordering of tactics in that matrix.

        Returns
        -------
        dict
            a list of tactics for each matrix
        """
        tactics = {}
        matrices = self.src.query([
            Filter('type', '=', 'x-mitre-matrix'),
        ])
        for i in range(len(matrices)):
            tactics[matrices[i]['name']] = []
            for tactic_id in matrices[i]['tactic_refs']:
                tactics[matrices[i]['name']].append(self.src.get(tactic_id))
        
        return tactics

    def get_objects_created_after(self, timestamp: str, remove_revoked_deprecated=False) -> list:
        """Retrieve objects which have been created after a given time.

        Parameters
        ----------
        timestamp : str
            timestamp to search (e.g. "2018-10-01T00:14:20.652Z")
        remove_revoked_deprecated : bool, optional
            remove revoked or deprecated objects from the query, by default False

        Returns
        -------
        list
            a list of stix2.v20.sdo._DomainObject or CustomStixObject objects created after the given time
        """
        objects = self.src.query([ Filter('created', '>', timestamp) ])
        if remove_revoked_deprecated:
            objects = self.remove_revoked_deprecated(objects)
        return objects

    def get_objects_modified_after(self, timestamp: str, remove_revoked_deprecated=False) -> list:
        """Retrieve objects which have been modified after a given time.

        Parameters
        ----------
        timestamp : str
            timestamp to search (e.g. "2018-10-01T00:14:20.652Z")
        remove_revoked_deprecated : bool, optional
            remove revoked or deprecated objects from the query, by default False

        Returns
        -------
        list
            a list of stix2.v20.sdo._DomainObject or CustomStixObject objects created after the given time
        """
        objects = self.src.query([ Filter('modified', '>', timestamp) ])
        if remove_revoked_deprecated:
            objects = self.remove_revoked_deprecated(objects)
        return objects

    def get_techniques_used_by_group_software(self, group_stix_id: str) -> list:
        """Get techniques used by a group's software.
        
        Because a group uses software, and software uses techniques, groups can be considered indirect users 
        of techniques used by their software. These techniques are oftentimes distinct from the techniques 
        used directly by a group, although there are occasionally intersections in these two sets of techniques.

        Parameters
        ----------
        group_stix_id : str
            the STIX ID of the group object

        Returns
        -------
        list
            a list of AttackPattern objects used by the group's software.
        """
        # get the malware, tools that the group uses
        group_uses = [
            r for r in self.src.relationships(group_stix_id, 'uses', source_only=True)
            if get_type_from_id(r.target_ref) in ['malware', 'tool']
        ]

        # get the technique stix ids that the malware, tools use
        source_refs = [r.target_ref for r in group_uses]
        software_uses = self.src.query([
            Filter('type', '=', 'relationship'),
            Filter('relationship_type', '=', 'uses'),
            Filter('source_ref', 'in', source_refs)
        ])

        # get the techniques themselves
        technique_ids = [r.target_ref for r in software_uses]
        return self.src.query([
            Filter('type', '=', 'attack-pattern'),
            Filter('id', 'in', technique_ids)
        ])
        
    ###################################
    # Get STIX Object by Value
    ###################################

    def get_object_by_stix_id(self, stix_id: str) -> object:
        """Retrieve a single object by STIX ID.

        Parameters
        ----------
        stix_id : str
            the STIX ID of the object to retrieve

        Returns
        -------
        stix2.v20.sdo._DomainObject | CustomStixObject
            the STIX Domain Object specified by the STIX ID
        """
        object = self.src.get(stix_id)
        return StixObjectFactory(object)

    def get_object_by_attack_id(self, attack_id: str, object_type: str) -> object:
        """Retrieve a single object by its ATT&CK ID

        Parameters
        ----------
        attack_id : str
            the ATT&CK ID of the object to retrieve
        object_type : str
            the STIX object type (must be 'attack-pattern', 'malware', 'tool', 'intrusion-set',
            'campaign', 'course-of-action', 'x-mitre-matrix', 'x-mitre-tactic',
            'x-mitre-data-source', or 'x-mitre-data-component')

        Returns
        -------
        stix2.v20.sdo._DomainObject | CustomStixObject
            the STIX Domain Object specified by the ATT&CK ID
        """
        # validate type
        if object_type not in self.stix_types:
            raise ValueError(f"object_type must be one of {self.stix_types}")
        
        object = self.src.query([
            Filter('external_references.external_id', '=', attack_id),
            Filter('type', '=', object_type),
        ])[0]
        return StixObjectFactory(object)

    def get_object_by_name(self, name: str, object_type: str) -> object:
        """Retrieve an object by name

        Parameters
        ----------
        name : str
            the name of the object to retrieve
        object_type : str
            the STIX object type (must be 'attack-pattern', 'malware', 'tool', 'intrusion-set',
            'campaign', 'course-of-action', 'x-mitre-matrix', 'x-mitre-tactic',
            'x-mitre-data-source', or 'x-mitre-data-component')

        Returns
        -------
        stix2.v20.sdo._DomainObject | CustomStixObject
            the STIX Domain Object specified by the name and type
        """
        # validate type
        if object_type not in self.stix_types:
            raise ValueError(f"object_type must be one of {self.stix_types}")

        filter = [
            Filter('type', '=', object_type),
            Filter('name', '=', name)
        ]
        object = self.src.query(filter)[0]
        return StixObjectFactory(object)

    def get_group_by_alias(self, alias: str) -> object:
        """Retrieve the group corresponding to a given alias

        Parameters
        ----------
        alias : str
            the alias of the group

        Returns
        -------
        stix2.v20.sdo.IntrusionSet
            the IntrusionSet object corresponding to the alias
        """
        filter = [
            Filter('type', '=', 'intrusion-set'),
            Filter('aliases', 'contains', alias)
        ]
        return self.src.query(filter)[0]

    def get_campaign_by_alias(self, alias: str) -> object:
        """Retrieve the campaign corresponding to a given alias

        Parameters
        ----------
        alias : str
            the alias of the campaign

        Returns
        -------
        stix2.v20.sdo.Campaign
            the Campaign object corresponding to the alias
        """
        filter = [
            Filter('type', '=', 'campaign'),
            Filter('aliases', 'contains', alias)
        ]
        return self.src.query(filter)[0]

    def get_software_by_alias(self, alias: str) -> object:
        """Retrieve the software corresponding to a given alias

        Parameters
        ----------
        alias : str
            the alias of the software

        Returns
        -------
        stix2.v20.sdo.Tool | stix2.v20.sdo.Malware
            the Tool or Malware object corresponding to the alias
        """
        malware_filter = [
            Filter('type', '=', 'malware'),
            Filter('x_mitre_aliases', 'contains', alias)
        ]
        tool_filter = [
            Filter('type', '=', 'tool'),
            Filter('x_mitre_aliases', 'contains', alias)
        ]
        software = list(chain.from_iterable(
            self.src.query(f) for f in [
                malware_filter,
                tool_filter
            ]
        ))[0]
        return software

    ###################################
    # Get Object Information
    ###################################

    def get_attack_id(self, stix_id: str) -> str:
        """Get the ATT&CK ID of the object with the given STIX ID

        Parameters
        ----------
        stix_id : str
            the STIX ID of the object

        Returns
        -------
        str
            the ATT&CK ID of the object
        """
        obj = self.get_object_by_stix_id(stix_id)
        external_references = obj.get('external_references')
        if external_references:
            attack_source = external_references[0]
            if attack_source.get('external_id') and attack_source.get('source_name') == 'mitre-attack':
                return attack_source['external_id']
        return None

    def get_object_type(self, stix_id: str) -> str:
        """Get the object type by STIX ID

        Parameters
        ----------
        stix_id : str
            the STIX ID of the object

        Returns
        -------
        str
            the type of the object
        """
        return get_type_from_id(stix_id)

    ###################################
    # Relationship Section
    ###################################

    def get_related(self, source_type: str, relationship_type: str, target_type: str, reverse: bool = False) -> dict:
        """Build relationship mappings

        Parameters
        ----------
        source_type : str
            source type for the relationships, e.g. 'attack-pattern'
        relationship_type : str
            relationship type for the relationships, e.g. 'uses'
        target_type : str
            target type for the relationships, e.g. 'intrusion-set'
        reverse : bool, optional
            build reverse mapping of target to source, by default False

        Returns
        -------
        dict
            if reverse=False, relationship mapping of source_object_id => [{target_object, relationship}]; 
            if reverse=True, relationship mapping of target_object_id => [{source_object, relationship}]
        """
        relationships = self.src.query([
            Filter('type', '=', 'relationship'),
            Filter('relationship_type', '=', relationship_type),
            Filter('revoked', '=', False),
        ])
        relationships = self.remove_revoked_deprecated(relationships)

        # stix_id => [ { relationship, related_object_id } for each related object ]
        id_to_related = {}

        # build the dict
        for relationship in relationships:
            if source_type in relationship.source_ref and target_type in relationship.target_ref:
                if (relationship.source_ref in id_to_related and not reverse) or (relationship.target_ref in id_to_related and reverse):
                    # append to existing entry
                    if not reverse:
                        id_to_related[relationship.source_ref].append({
                            'relationship': relationship,
                            'id': relationship.target_ref
                        })
                    else:
                        id_to_related[relationship.target_ref].append({
                            'relationship': relationship,
                            'id': relationship.source_ref
                        })
                else:
                    # create a new entry
                    if not reverse:
                        id_to_related[relationship.source_ref] = [{
                            'relationship': relationship,
                            'id': relationship.target_ref
                        }]
                    else:
                        id_to_related[relationship.target_ref] = [{
                            'relationship': relationship,
                            'id': relationship.source_ref
                        }]

        # all objects of relevant type
        if not reverse:
            targets = self.src.query([
                Filter('type', '=', target_type),
                Filter('revoked', '=', False)
            ])
        else:
            targets = self.src.query([
                Filter('type', '=', source_type),
                Filter('revoked', '=', False)
            ])

        # build lookup of stixID to stix object
        id_to_target = {}
        for target in targets:
            id_to_target[target['id']] = target

        # build final output mappings
        output = {}
        for stix_id in id_to_related:
            value = []
            for related in id_to_related[stix_id]:
                if not related['id'] in id_to_target:
                    continue  # targeting a revoked object
                value.append({
                    'object': StixObjectFactory(id_to_target[related['id']]),
                    'relationship': related['relationship']
                })
            output[stix_id] = value
        return output

    def merge(self, map_a: dict, map_b: dict) -> dict:
        """Merge two relationship mappings resulting from `get_related()`

        Parameters
        ----------
        map_a : dict
            the first relationship mapping
        map_b : dict
            the second relationship mapping

        Returns
        -------
        dict
            the merged relationship mapping
        """
        for id in map_b:
            if id in map_a:
                map_a[id].extend(map_b[id])
            else:
                map_a[id] = map_b[id]
        return map_a

    ###################################
    # Software/Group Relationships
    ###################################

    def get_software_used_by_groups(self) -> dict:
        """Get software used by groups

        Returns
        -------
        dict
            a mapping of group_id => {software, relationship} for each software used by the group and each software used 
            by campaigns attributed to the group
        """
        # get all software used by groups
        tools_used_by_group = self.get_related('intrusion-set', 'uses', 'tool')
        malware_used_by_group = self.get_related('intrusion-set', 'uses', 'malware')
        software_used_by_group = self.merge(tools_used_by_group, malware_used_by_group) # group_id -> {software, relationship}

        # get groups attributing to campaigns and all software used by campaigns
        tools_used_by_campaign = self.get_related('campaign', 'uses', 'tool')
        malware_used_by_campaign = self.get_related('campaign', 'uses', 'malware')
        software_used_by_campaign = self.merge(tools_used_by_campaign, malware_used_by_campaign) # campaign_id => {software, relationship}

        campaigns_attributed_to_group = {
            'campaigns': self.get_related('campaign', 'attributed-to', 'intrusion-set', reverse=True), # group_id => {campaign, relationship}
            'software': software_used_by_campaign # campaign_id => {software, relationship}
        }

        for group_id in campaigns_attributed_to_group['campaigns']:
            software_used_by_campaigns = []
            # check if attributed campaign is using software
            for campaign in campaigns_attributed_to_group['campaigns'][group_id]:
                campaign_id = campaign['object']['id']
                if campaign_id in campaigns_attributed_to_group['software']:
                    software_used_by_campaigns.extend(campaigns_attributed_to_group['software'][campaign_id])
            
            # update software used by group to include software used by a groups attributed campaign
            if group_id in software_used_by_group:
                software_used_by_group[group_id].extend(software_used_by_campaigns)
            else:
                software_used_by_group[group_id] = software_used_by_campaigns
        return software_used_by_group

    def get_software_used_by_group_with_id(self, stix_id: str) -> list:
        """Get all software used by a single group

        Note: this method is not recommended for retrieving large numbers of related objects.
        If retrieving a large number of objects, call `get_software_used_by_groups()` directly,
        then access the data from the dictionary result:
        
            software_used = get_software_used_by_groups()

            software_used[group_stix_id]

        Parameters
        ----------
        stix_id : str
            the STIX ID of the group

        Returns
        -------
        list
            a list of {software, relationship} for each software used by the group and each software used 
            by campaigns attributed to the group
        """
        software_used_by_groups = self.get_software_used_by_groups()
        return software_used_by_groups[stix_id] if stix_id in software_used_by_groups else []

    def get_groups_using_software(self) -> dict:
        """Get groups using software

        Returns
        -------
        dict
            a mapping of software_id => {group, relationship} for each group using the software and each attributed campaign
            using the software
        """
        # get all groups using software
        groups_using_tool = self.get_related('intrusion-set', 'uses', 'tool', reverse=True)
        groups_using_malware = self.get_related('intrusion-set', 'uses', 'malware', reverse=True)
        groups_using_software = self.merge(groups_using_tool, groups_using_malware) # software_id => {group, relationship}

        # get campaigns attributed to groups and all campaigns using software
        campaigns_using_tools = self.get_related('campaign', 'uses', 'tool', reverse=True)
        campaigns_using_malware = self.get_related('campaign', 'uses', 'malware', reverse=True)
        campaigns_using_software = self.merge(campaigns_using_tools, campaigns_using_malware) # software_id => {campaign, relationship}

        groups_attributing_to_campaigns = {
            'campaigns': campaigns_using_software, # software_id => {campaign, relationship}
            'groups': self.get_related('campaign', 'attributed-to', 'intrusion-set') # campaign_id => {group, relationship}
        }

        for software_id in groups_attributing_to_campaigns['campaigns']:
            groups_attributed_to_campaigns = []
            # check if campaign is attributed to group
            for campaign in groups_attributing_to_campaigns['campaigns'][software_id]:
                campaign_id = campaign['object']['id']
                if campaign_id in groups_attributing_to_campaigns['groups']:
                    groups_attributed_to_campaigns.extend(groups_attributing_to_campaigns['groups'][campaign_id])
            
            # update groups using software to include software used by a groups attributed campaign
            if software_id in groups_using_software:
                groups_using_software[software_id].extend(groups_attributed_to_campaigns)
            else:
                groups_using_software[software_id] = groups_attributed_to_campaigns
        return groups_using_software

    def get_groups_using_software_with_id(self, stix_id: str) -> list:
        """Get all groups using a single software

        Note: this method is not recommended for retrieving large numbers of related objects.
        If retrieving a large number of objects, call `get_groups_using_software()` directly,
        then access the data from the dictionary result:
        
            groups_using_software = get_groups_using_software()
            
            groups_using_software[software_stix_id]

        Parameters
        ----------
        stix_id : str
            the STIX ID of the software

        Returns
        -------
        list
            a list of {group, relationship} for each group using the software and each attributed campaign
            using the software
        """
        groups_using_software = self.get_groups_using_software()
        return groups_using_software[stix_id] if stix_id in groups_using_software else []

    ###################################
    # Software/Campaign Relationships
    ###################################

    def get_software_used_by_campaigns(self) -> dict:
        """Get software used by campaigns

        Returns
        -------
        dict
            a mapping of campaign_id => {software, relationship} for each software used by the campaign
        """
        tools_used_by_campaign = self.get_related('campaign', 'uses', 'tool')
        malware_used_by_campaign = self.get_related('campaign', 'uses', 'malware')
        software_used_by_campaign = self.merge(tools_used_by_campaign, malware_used_by_campaign)
        return software_used_by_campaign

    def get_software_used_by_campaign_with_id(self, stix_id: str) -> list:
        """Get all software used by a single campaign

        Note: this method is not recommended for retrieving large numbers of related objects.
        If retrieving a large number of objects, call `get_software_used_by_campaigns()` directly,
        then access the data from the dictionary result:
        
            software_used = get_software_used_by_campaigns()
            
            software_used[campaign_stix_id]

        Parameters
        ----------
        stix_id : str
            the STIX ID of the campaign

        Returns
        -------
        list
            a list of {software, relationship} for each software used by the campaign
        """
        software_used_by_campaigns = self.get_software_used_by_campaigns()
        return software_used_by_campaigns[stix_id] if stix_id in software_used_by_campaigns else []

    def get_campaigns_using_software(self) -> dict:
        """Get campaigns using software

        Returns
        -------
        dict
            a mapping of software_id => {campaign, relationship} for each campaign using the software
        """
        campaigns_using_tool = self.get_related('campaign', 'uses', 'tool', reverse=True)
        campaigns_using_malware = self.get_related('campaign', 'uses', 'malware', reverse=True)
        campaigns_using_software = self.merge(campaigns_using_tool, campaigns_using_malware)
        return campaigns_using_software

    def get_campaigns_using_software_with_id(self, stix_id: str) -> list:
        """Get all campaigns using a single software

        Note: this method is not recommended for retrieving large numbers of related objects.
        If retrieving a large number of objects, call `get_campaigns_using_software()` directly,
        then access the data from the dictionary result:
        
            campaigns_using_software = get_campaigns_using_software()
            
            campaigns_using_software[software_stix_id]

        Parameters
        ----------
        stix_id : str
            the STIX ID of the software

        Returns
        -------
        list
            a list of {campaign, relationship} for each campaign using the software
        """
        campaigns_using_software = self.get_campaigns_using_software()
        return campaigns_using_software[stix_id] if stix_id in campaigns_using_software else []


    ###################################
    # Campaign/Group Relationships
    ###################################

    def get_groups_attributing_to_campaigns(self) -> dict:
        """Get groups attributing to campaigns

        Returns
        -------
        dict
            a mapping of campaign_id => {group, relationship} for each group attributing to the campaign
        """
        return self.get_related('campaign', 'attributed-to', 'intrusion-set')
    
    def get_groups_attributing_to_campaign_with_id(self, stix_id: str) -> list:
        """Get all groups attributing to a single campaign

        Note: this method is not recommended for retrieving large numbers of related objects.
        If retrieving a large number of objects, call `get_groups_attributing_to_campaigns()` directly,
        then access the data from the dictionary result:
        
            groups_attributing = get_groups_attributing_to_campaigns()
            
            groups_attributing[campaign_stix_id]

        Parameters
        ----------
        stix_id : str
            the STIX ID of the campaign

        Returns
        -------
        list
            a list of {group, relationship} for each group attributing to the campaign
        """
        groups_attributing_to_campaigns = self.get_groups_attributing_to_campaigns()
        return groups_attributing_to_campaigns[stix_id] if stix_id in groups_attributing_to_campaigns else []

    def get_campaigns_attributed_to_groups(self) -> dict:
        """Get campaigns attributed to groups

        Returns
        -------
        dict
            a mapping of group_id => {campaign, relationship} for each campaign attributed to the group
        """
        return self.get_related('campaign', 'attributed-to', 'intrusion-set', reverse=True)

    def get_campaigns_attributed_to_group_with_id(self, stix_id: str) -> list:
        """Get all campaigns attributed to a single group

        Note: this method is not recommended for retrieving large numbers of related objects.
        If retrieving a large number of objects, call `get_campaigns_attributed_to_groups()` directly,
        then access the data from the dictionary result:
        
            campaigns_attributed = get_campaigns_attributed_to_groups()
            
            campaigns_attributed[group_stix_id]

        Parameters
        ----------
        stix_id : str
            the STIX ID of the group

        Returns
        -------
        list
            a list of {campaign, relationship} for each campaign attributed to the group
        """
        campaigns_attributed_to_groups = self.get_campaigns_attributed_to_groups()
        return campaigns_attributed_to_groups[stix_id] if stix_id in campaigns_attributed_to_groups else []

    ###################################
    # Technique/Group Relationships
    ###################################

    def get_techniques_used_by_groups(self) -> dict:
        """Get techniques used by groups

        Returns
        -------
        dict
            a mapping of group_id => {technique, relationship} for each technique used by the group and 
            each technique used by campaigns attributed to the group
        """
        # get all techniques used by groups
        techniques_used_by_groups = self.get_related('intrusion-set', 'uses', 'attack-pattern') # group_id => {technique, relationship}

        # get groups attributing to campaigns and all techniques used by campaigns
        campaigns_attributed_to_group = {
            'campaigns': self.get_related('campaign', 'attributed-to', 'intrusion-set', reverse=True), # group_id => {campaign, relationship}
            'techniques': self.get_related('campaign', 'uses', 'attack-pattern') # campaign_id => {technique, relationship}
        }

        for group_id in campaigns_attributed_to_group['campaigns']:
            techniques_used_by_campaigns = []
            # check if attributed campaign is using technique
            for campaign in campaigns_attributed_to_group['campaigns'][group_id]:
                campaign_id = campaign['object']['id']
                if campaign_id in campaigns_attributed_to_group['techniques']:
                    techniques_used_by_campaigns.extend(campaigns_attributed_to_group['techniques'][campaign_id])

            # update techniques used by groups to include techniques used by a groups attributed campaign
            if group_id in techniques_used_by_groups:
                techniques_used_by_groups[group_id].extend(techniques_used_by_campaigns)
            else:
                techniques_used_by_groups[group_id] = techniques_used_by_campaigns
        return techniques_used_by_groups

    def get_techniques_used_by_group_with_id(self, stix_id: str) -> list:
        """Get all techniques used by a single group

        Note: this method is not recommended for retrieving large numbers of related objects.
        If retrieving a large number of objects, call `get_techniques_used_by_groups()` directly,
        then access the data from the dictionary result:
        
            techniques_used = get_techniques_used_by_groups()
            
            techniques_used[group_stix_id]

        Parameters
        ----------
        stix_id : str
            the STIX ID of the group

        Returns
        -------
        list
            a list of {technique, relationship} for each technique used by the group and 
            each technique used by campaigns attributed to the group
        """
        techniques_used_by_groups = self.get_techniques_used_by_groups()
        return techniques_used_by_groups[stix_id] if stix_id in techniques_used_by_groups else []

    def get_groups_using_techniques(self) -> dict:
        """Get groups using techniques

        Returns
        -------
        dict
            a mapping of technique_id => {group, relationship} for each group using the technique and each campaign attributed to 
            groups using the technique
        """
        # get all groups using techniques
        groups_using_techniques = self.get_related('intrusion-set', 'uses', 'attack-pattern', reverse=True) # technique_id => {group, relationship}

        # get campaigns attributed to groups and all campaigns using techniques
        groups_attributing_to_campaigns = {
            'campaigns': self.get_related('campaign', 'uses', 'attack-pattern', reverse=True), # technique_id => {campaign, relationship}
            'groups': self.get_related('campaign', 'attributed-to', 'intrusion-set') # campaign_id => {group, relationship}
        }

        for technique_id in groups_attributing_to_campaigns['campaigns']:
            campaigns_attributed_to_group = []
            # check if campaign is attributed to group
            for campaign in groups_attributing_to_campaigns['campaigns'][technique_id]:
                campaign_id = campaign['object']['id']
                if campaign_id in groups_attributing_to_campaigns['groups']:
                    campaigns_attributed_to_group.extend(groups_attributing_to_campaigns['groups'][campaign_id])
            
            # update groups using techniques to include techniques used by a groups attributed campaign
            if technique_id in groups_using_techniques:
                groups_using_techniques[technique_id].extend(campaigns_attributed_to_group)
            else:
                groups_using_techniques[technique_id] = campaigns_attributed_to_group
        return groups_using_techniques

    def get_groups_using_technique_with_id(self, stix_id: str) -> list:
        """Get all groups using a single technique

        Note: this method is not recommended for retrieving large numbers of related objects.
        If retrieving a large number of objects, call `get_groups_using_techniques()` directly,
        then access the data from the dictionary result:
        
            groups_using_techniques = get_groups_using_techniques()
            
            groups_using_techniques[technique_stix_id]

        Parameters
        ----------
        stix_id : str
            the STIX ID of the technique

        Returns
        -------
        list
            a list of {group, relationship} for each group using the technique and each campaign attributed to 
            groups using the technique
        """
        groups_using_techniques = self.get_groups_using_techniques()
        return groups_using_techniques[stix_id] if stix_id in groups_using_techniques else []

    ###################################
    # Technique/Campaign Relationships
    ###################################

    def get_techniques_used_by_campaigns(self) -> dict:
        """Get techniques used by campaigns

        Returns
        -------
        dict
            a mapping of campaign_id => {technique, relationship} for each technique used by the campaign
        """
        return self.get_related('campaign', 'uses', 'attack-pattern')

    def get_techniques_used_by_campaign_with_id(self, stix_id: str) -> list:
        """Get all techniques used by a single campaign

        Note: this method is not recommended for retrieving large numbers of related objects.
        If retrieving a large number of objects, call `get_techniques_used_by_campaigns()` directly,
        then access the data from the dictionary result:
        
            techniques_used = get_techniques_used_by_campaigns()
            
            techniques_used[campaign_stix_id]

        Parameters
        ----------
        stix_id : str
            the STIX ID of the campaign

        Returns
        -------
        list
            a list of {technique, relationship} for each technique used by the campaign
        """
        techniques_used_by_campaigns = self.get_techniques_used_by_campaigns()
        return techniques_used_by_campaigns[stix_id] if stix_id in techniques_used_by_campaigns else []

    def get_campaigns_using_techniques(self) -> dict:
        """Get campaigns using techniques

        Returns
        -------
        dict
            a mapping of technique_id => {campaign, relationship} for each campaign using the technique
        """
        return self.get_related('campaign', 'uses', 'attack-pattern', reverse=True)

    def get_campaigns_using_technique_with_id(self, stix_id: str) -> list:
        """Get all campaigns using a single technique

        Note: this method is not recommended for retrieving large numbers of related objects.
        If retrieving a large number of objects, call `get_campaigns_using_techniques()` directly,
        then access the data from the dictionary result:
        
            campaigns_using_techniques = get_campaigns_using_techniques()
            
            campaigns_using_techniques[technique_stix_id]

        Parameters
        ----------
        stix_id : str
            the STIX ID of the technique

        Returns
        -------
        list
            a list of {campaign, relationship} for each campaign using the technique
        """
        campaigns_using_techniques = self.get_campaigns_using_techniques()
        return campaigns_using_techniques[stix_id] if stix_id in campaigns_using_techniques else []

    ###################################
    # Technique/Software Relationships
    ###################################

    def get_techniques_used_by_software(self) -> dict:
        """Get techniques used by software

        Returns
        -------
        dict
            a mapping of software_id => {technique, relationship} for each technique used by the software
        """
        techniques_by_tool = self.get_related('tool', 'uses', 'attack-pattern')
        techniques_by_malware = self.get_related('malware', 'uses', 'attack-pattern')
        return {**techniques_by_tool, **techniques_by_malware}

    def get_techniques_used_by_software_with_id(self, stix_id: str) -> list:
        """Get all techniques used by a single software

        Note: this method is not recommended for retrieving large numbers of related objects.
        If retrieving a large number of objects, call `get_techniques_used_by_software()` directly,
        then access the data from the dictionary result:
        
            techniques_used = get_techniques_used_by_software()
            
            techniques_used[software_stix_id]

        Parameters
        ----------
        stix_id : str
            the STIX ID of the software

        Returns
        -------
        list
            a list of {technique, relationship} for each technique used by the software
        """
        techniques_used_by_software = self.get_techniques_used_by_software()
        return techniques_used_by_software[stix_id] if stix_id in techniques_used_by_software else []

    def get_software_using_techniques(self) -> dict:
        """Get software using technique

        Returns
        -------
        dict
            a mapping of technique_id => {software, relationship} for each software using the technique
        """
        tools_by_technique_id = self.get_related('tool', 'uses', 'attack-pattern', reverse=True)
        malware_by_technique_id = self.get_related('malware', 'uses', 'attack-pattern', reverse=True)
        return {**tools_by_technique_id, **malware_by_technique_id}

    def get_software_using_technique_with_id(self, stix_id: str) -> list:
        """Get all software using a single technique

        Note: this method is not recommended for retrieving large numbers of related objects.
        If retrieving a large number of objects, call `get_software_using_techniques()` directly,
        then access the data from the dictionary result:
        
            software_using_techniques = get_software_using_techniques()
            
            software_using_techniques[technique_stix_id]

        Parameters
        ----------
        stix_id : str
            the STIX ID of the technique

        Returns
        -------
        list
            a list of {software, relationship} for each software using the technique
        """
        software_using_techniques = self.get_software_using_techniques()
        return software_using_techniques[stix_id] if stix_id in software_using_techniques else []

    ###################################
    # Technique/Mitigation Relationships
    ###################################

    def get_techniques_mitigated_by_mitigations(self) -> dict:
        """Get techniques mitigated by mitigations

        Returns
        -------
        dict
            a mapping of mitigation_id => {technique, relationship} for each technique mitigated by the mitigation
        """
        return self.get_related('course-of-action', 'mitigates', 'attack-pattern')
    
    def get_techniques_mitigated_by_mitigation_with_id(self, stix_id: str) -> list:
        """Get all techniques being mitigated by a single mitigation

        Note: this method is not recommended for retrieving large numbers of related objects.
        If retrieving a large number of objects, call `get_techniques_mitigated_by_mitigations()` directly,
        then access the data from the dictionary result:
        
            techniques_mitigated = get_techniques_mitigated_by_mitigations()
            
            techniques_mitigated[mitigation_stix_id]

        Parameters
        ----------
        stix_id : str
            the STIX ID of the mitigation

        Returns
        -------
        list
            a list of {technique, relationship} for each technique mitigated by the mitigation
        """
        techniques_mitigated_by_mitigations = self.get_techniques_mitigated_by_mitigations()
        return techniques_mitigated_by_mitigations[stix_id] if stix_id in techniques_mitigated_by_mitigations else []

    def get_mitigations_mitigating_techniques(self) -> dict:
        """Get mitigations mitigating techniques

        Returns
        -------
        dict
            a mapping of technique_id => {mitigation, relationship} for each mitigation mitigating the technique
        """
        return self.get_related('course-of-action', 'mitigates', 'attack-pattern', reverse=True)

    def get_mitigations_mitigating_technique_with_id(self, stix_id: str) -> list:
        """Get all mitigations mitigating a single technique

        Note: this method is not recommended for retrieving large numbers of related objects.
        If retrieving a large number of objects, call `get_mitigations_mitigating_techniques()` directly,
        then access the data from the dictionary result:
        
            mitigations_mitigating = get_mitigations_mitigating_techniques()
            
            mitigations_mitigating[technique_stix_id]

        Parameters
        ----------
        stix_id : str
            the STIX ID of the technique

        Returns
        -------
        list
            a list of {mitigation, relationship} for each mitigation mitigating the technique
        """

    ###################################
    # Technique/Subtechnique Relationships
    ###################################

    def get_parent_techniques_of_subtechniques(self) -> dict:
        """Get parent techniques of subtechniques

        Returns
        -------
        dict
            a mapping of subtechnique_id => {technique, relationship} describing the parent technique of the subtechnique
        """
        return self.get_related('attack-pattern', 'subtechnique-of', 'attack-pattern')

    def get_parent_technique_of_subtechnique_with_id(self, stix_id: str) -> dict:
        """Get the parent technique of a single subtechnique

        Note: this method is not recommended for retrieving large numbers of related objects.
        If retrieving a large number of objects, call `get_parent_technique_of_subtechniques()` directly,
        then access the data from the dictionary result:
        
            parent_techniques = get_parent_technique_of_subtechniques()
            
            parent_techniques[subtechnique_stix_id]

        Parameters
        ----------
        stix_id : str
            the STIX ID of the subtechnique

        Returns
        -------
        dict
            {parent technique, relationship} describing the parent technique of the subtechnique
        """
        parent_techniques_of_subtechniques = self.get_parent_techniques_of_subtechniques()
        return parent_techniques_of_subtechniques[stix_id] if stix_id in parent_techniques_of_subtechniques else []

    def get_subtechniques_of_techniques(self) -> dict:
        """Get subtechniques of techniques

        Returns
        -------
        dict
            a mapping of technique_id => {subtechnique, relationship} for each subtechnique of the technique
        """
        return self.get_related('attack-pattern', 'subtechnique-of', 'attack-pattern', reverse=True)

    def get_subtechniques_of_technique_with_id(self, stix_id: str) -> list:
        """Get all subtechniques of a single technique

        Note: this method is not recommended for retrieving large numbers of related objects.
        If retrieving a large number of objects, call `get_subtechniques_of_techniques()` directly,
        then access the data from the dictionary result:
        
            subtechniques = get_subtechniques_of_techniques()
            
            subtechniques[technique_stix_id]

        Parameters
        ----------
        stix_id : str
            the STIX ID of the technique

        Returns
        -------
        list
            a list of {subtechnique, relationship} for each subtechnique of the technique
        """
        subtechniques_of_techniques = self.get_subtechniques_of_techniques()
        return subtechniques_of_techniques[stix_id] if stix_id in subtechniques_of_techniques else []

    ###################################
    # Technique/Data Component Relationships
    ###################################

    def get_techniques_detected_by_datacomponents(self) -> dict:
        """Get techniques detected by data components
        Returns
        -------
        dict
            a mapping of datacomponent_id => {technique, relationship} describing the detections of the data component
        """
        return self.get_related('x-mitre-data-component', 'detects', 'attack-pattern')
    
    def get_techniques_detected_by_datacomponent_with_id(self, stix_id: str) -> list:
        """Get all techniques detected by a single data component

        Note: this method is not recommended for retrieving large numbers of related objects.
        If retrieving a large number of objects, call `get_techniques_detected_by_datacomponents()` directly,
        then access the data from the dictionary result:
        
            techniques_detected = get_techniques_detected_by_datacomponents()
            
            techniques_detected[datacomponent_stix_id]

        Parameters
        ----------
        stix_id : str
            the STIX ID of the data component

        Returns
        -------
        list
            a list of {technique, relationship} describing the detections of the data component
        """
        techniques_detected_by_datacomponents = self.get_techniques_detected_by_datacomponents()
        return techniques_detected_by_datacomponents[stix_id] if stix_id in techniques_detected_by_datacomponents else []

    def get_datacomponents_detecting_techniques(self) -> dict:
        """Get data components detecting techniques

        Returns
        -------
        dict
            a mapping of technique_id => {datacomponent, relationship} describing the data components that can detect the technique
        """
        return self.get_related('x-mitre-data-component', 'detects', 'attack-pattern', reverse=True)

    def get_datacomponents_detecting_technique_with_id(self, stix_id: str) -> list:
        """Get all data components detecting a single technique

        Note: this method is not recommended for retrieving large numbers of related objects.
        If retrieving a large number of objects, call `get_datacomponents_detecting_techniques()` directly,
        then access the data from the dictionary result:
        
            datacomponents_detecting = get_datacomponents_detecting_techniques()
            
            datacomponents_detecting[technique_stix_id]

        Parameters
        ----------
        stix_id : str
            the STIX ID of the technique

        Returns
        -------
        list
            a list of {datacomponent, relationship} describing the data components that can detect the technique
        """
        datacomponents_detecting_techniques = self.get_datacomponents_detecting_techniques()
        return datacomponents_detecting_techniques[stix_id] if stix_id in datacomponents_detecting_techniques else []

    def get_revoked_by(self, stix_id: str) -> object:
        """Retrieve the revoking object.

        Parameters
        ----------
        stix_id : str
            the STIX ID of the object that has been revoked

        Returns
        -------
        object
            the object that the given object was revoked by
        """
        relations = self.src.relationships(stix_id, 'revoked-by', source_only=True)
        revoked_by = self.src.query([
            Filter('id', 'in', [r.target_ref for r in relations]),
            Filter('revoked', '=', False)
        ])
        if revoked_by is not None:
            revoked_by = revoked_by[0]

        return revoked_by
