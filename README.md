# ContainerManager
Simple Maya Container Manager

**Uses only Maya's OM2 Python API**
****
As the maya container UI, is extremly frustrating, 
I wrote a simple and intuative UI for container interaction, 
and easy to use wrapper module for containers.
****
The container module can also be used to easily modify containers
* Add / Remove Container
* Add / Remove Objects in a container
* Expose / Hide Objects in a container
* Select the container that a selected asset is contained to 

****
#### Setup
Copy the root of this repo ```ContainerManager``` into your 
system ```PYTHONPATH``` environemnt variables

In the script editor run the following

```python
from ContainerManager import ui as cm

cm.CreateContainerManager()
```

Please feel free to comment, report bugs, add to the repo and 
suggest modifications and additions. The more the merrier

****
### TODO

- [ ] Expose / Hide parameters from the container.
- [ ] List UI to view assets in the container.
- [ ] UI Icons, for simpler user interaction.
- [ ] Overall code tidy up and refactor.
- [ ] Pop-up small container name dialog
