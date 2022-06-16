document.addEventListener("DOMContentLoaded", ()=>{   
    boxesTable = document.querySelector("#pills-all")
    boxesTable.replaceChildren()

    warehouseButtons = document.querySelectorAll(".js-select-warehouse")
    for (warehouseButton of warehouseButtons){
        warehouseButton.addEventListener("click", fetch_data)
    }

    buttonAllAreas = document.querySelector("#pills-all-tab")
    buttonAllAreas.addEventListener("click", (event)=>{
        pills = document.querySelectorAll(".js-box-row")
        for (pill of pills){
            pill.classList.remove("d-none")
        }
    })

    buttonTo3 = document.querySelector("#pills-to3-tab")
    buttonTo3.addEventListener("click", (event)=>{
        pills = document.querySelectorAll(".js-box-row")
        for (pill of pills){
            if(pill.classList.contains("js-area-to-3"))
                pill.classList.remove("d-none")
            else
                pill.classList.add("d-none")
        }
    })
    buttonTo10 = document.querySelector("#pills-to10-tab")
    buttonTo10.addEventListener("click", (event)=>{
        pills = document.querySelectorAll(".js-box-row")
        for (pill of pills){
            if(pill.classList.contains("js-area-to-10"))
                pill.classList.remove("d-none")
            else
                pill.classList.add("d-none")
        }
    })
    buttonFrom10 = document.querySelector("#pills-from10-tab")
    buttonFrom10.addEventListener("click", (event)=>{
        pills = document.querySelectorAll(".js-box-row")
        for (pill of pills){
            if(pill.classList.contains("js-area-from-10"))
                pill.classList.remove("d-none")
            else
                pill.classList.add("d-none")
        }
    })

    leaseDuration = document.querySelector("#leaseDuration")
    leasePrice = document.querySelector("#leasePrice")
    duration.addEventListener("change", (event)=>{
        leaseDuration.textContent = event.target.value + " месяц(ев)"
        leasePrice.textContent = (parseInt(event.target.value) * parseFloat(modalBoxPrice.dataset.rate)) + " ₽"
    })

    inputCode = document.querySelector("#code")
    modalBoxWhAddress = document.querySelector("#boxWhAddress")
    modalBoxCode = document.querySelector("#boxCode")
    modalBoxDims = document.querySelector("#boxDims")
    modalBoxArea = document.querySelector("#boxArea")
    modalBoxPrice = document.querySelector("#boxPrice")

    function fetch_data(event){
        id = event.currentTarget.dataset.warehouse

        if (boxesTable.dataset.current == id){
            console.log("Repeated fetch attempted. Skipping.")
            return
        }
        
        buttonTo3.classList.remove("active")
        buttonTo10.classList.remove("active")
        buttonFrom10.classList.remove("active")
        buttonAllAreas.classList.add("active")

        fetch("warehouse/"+id).then((response) => response.json()).then((data)=>{
            console.log("New data arrived... rebuilding DOM")
            boxesTable.dataset.current = id
            boxPills = []
            for (box of data.boxes){
                outerContainer = document.createElement("a")
                outerContainer.classList.add("js-box-row", "row", "text-decoration-none", "py-3", "px-4", "mt-5", "SelfStorage__boxlink")
                if(box.area<3)
                    outerContainer.classList.add("js-area-to-3")
                if(box.area<10)
                    outerContainer.classList.add("js-area-to-10")
                else
                    outerContainer.classList.add("js-area-from-10")

                floorCodeContainer = document.createElement("div")
                floorCodeContainer.classList.add("col-12", "col-md-4", "col-lg-3", "d-flex", "justify-content-center", "align-items-center")
                floorSpan = document.createElement("span")
                floorSpan.classList.add("SelfStorage_green", "fs_24", "me-2")
                floorSpan.textContent = box.floor + " эт."
                codeSpan = document.createElement("span")
                codeSpan.classList.add("fs_24")
                codeSpan.textContent = "№"+box.code

                floorCodeContainer.appendChild(floorSpan)
                floorCodeContainer.appendChild(codeSpan)


                areaContainer = document.createElement("div")
                areaContainer.classList.add("col-6", "col-md-4", "col-lg-3", "d-flex", "justify-content-center", "align-items-center")
                areaSpan = document.createElement("span")
                areaSpan.classList.add("fs_24")
                areaSpan.textContent = box.area + " м²"

                areaContainer.appendChild(areaSpan)
                

                dimensionsContainer = document.createElement("div")
                dimensionsContainer.classList.add("col-6", "col-md-4", "col-lg-3", "d-flex", "justify-content-center", "align-items-center")
                dimensionsSpan = document.createElement("span")
                dimensionsSpan.classList.add("fs_24")
                dimensionsSpan.textContent = box.dimensions + " м"

                dimensionsContainer.appendChild(dimensionsSpan)


                rateContainer = document.createElement("div")
                rateContainer.classList.add("col-12", "col-lg-3")
                rateSpan = document.createElement("span")
                rateSpan.classList.add("btn", "my-2", "w-100", "text-white", "fs_24", "SelfStorage__bg_orange", "SelfStorage__btn2_orange", "border-8")
                rateSpan.setAttribute("data-bs-toggle", "modal")
                rateSpan.setAttribute("data-bs-target", "#LeaseModal")
                rateSpan.textContent = box.rate + " ₽"

                rateSpan.addEventListener("click", (event)=>{
                    modalBoxWhAddress.textContent = box.warehouse_city+", "+box.warehouse_address
                    modalBoxCode.textContent = "№"+box.code
                    inputCode.value = box.code
                    modalBoxArea.textContent = box.area + " м²"
                    modalBoxDims.textContent = box.dimensions + " м"
                    modalBoxPrice.textContent = box.rate + " ₽"
                    modalBoxPrice.dataset.rate = box.rate
                })

                rateContainer.appendChild(rateSpan)


                outerContainer.appendChild(floorCodeContainer)
                outerContainer.appendChild(areaContainer)
                outerContainer.appendChild(dimensionsContainer)
                outerContainer.appendChild(rateContainer)
                boxPills.push(outerContainer)
            }

            boxesTable.replaceChildren(...boxPills)
        })
    }
})