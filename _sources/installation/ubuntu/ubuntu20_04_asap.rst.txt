**Installing ASAP on Ubuntu20.04**

:bdg-link-primary:`Download ASAP <https://github.com/computationalpathologygroup/ASAP/releases/download/ASAP-2.0-(Nightly)/ASAP-2.0-py38-Ubuntu2004.deb>`

:octicon:`package;0.8em;` Double click "ASAP-2.0-py38-Ubuntu2004.deb" and follow instruction in Ubuntu Software Centre. 

:octicon:`plug;0.8em;` Add ASAP python API to site packages:

.. code-block:: bash

    site_packages=`python -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])'`
    echo "/opt/ASAP/bin" > ${site_packages}/asap.pth

.. seealso:: `Alternative installation instructions <https://github.com/computationalpathologygroup/ASAP/releases>`_
