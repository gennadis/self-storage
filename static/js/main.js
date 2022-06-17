document.addEventListener("DOMContentLoaded", ()=>{   
    let selectedBox = undefined
    let present_boxes = []
    
    let boxesTable = document.querySelector("#pills-all")
    boxesTable.replaceChildren()

    let warehouseButtons = document.querySelectorAll(".js-select-warehouse")
    for (warehouseButton of warehouseButtons){
        warehouseButton.addEventListener("click", fetch_data)
    }

    let buttonAllAreas = document.querySelector("#pills-all-tab")
    buttonAllAreas.addEventListener("click", (event)=>{
        pills = document.querySelectorAll(".js-box-row")
        for (pill of pills){
            pill.classList.remove("d-none")
        }
    })

    let buttonTo3 = document.querySelector("#pills-to3-tab")
    buttonTo3.addEventListener("click", (event)=>{
        pills = document.querySelectorAll(".js-box-row")
        for (pill of pills){
            if(pill.classList.contains("js-area-to-3"))
                pill.classList.remove("d-none")
            else
                pill.classList.add("d-none")
        }
    })
    let buttonTo10 = document.querySelector("#pills-to10-tab")
    buttonTo10.addEventListener("click", (event)=>{
        pills = document.querySelectorAll(".js-box-row")
        for (pill of pills){
            if(pill.classList.contains("js-area-to-10"))
                pill.classList.remove("d-none")
            else
                pill.classList.add("d-none")
        }
    })
    let buttonFrom10 = document.querySelector("#pills-from10-tab")
    buttonFrom10.addEventListener("click", (event)=>{
        pills = document.querySelectorAll(".js-box-row")
        for (pill of pills){
            if(pill.classList.contains("js-area-from-10"))
                pill.classList.remove("d-none")
            else
                pill.classList.add("d-none")
        }
    })

    let warehousePreviewButtons = document.querySelectorAll(".js-select-warehouse")
    let warehouseBox = document.querySelector("#BOX")
    for (let whButton of warehousePreviewButtons){
      whButton.addEventListener("click",(event)=>{
        warehouseBox.scrollIntoView()
      })
    }

    let warehouseRentButtons = document.querySelectorAll(".js-rent-storage")
    let boxesList = document.querySelector("#pills-tabContent")
    for (let whButton of warehouseRentButtons){
      whButton.addEventListener("click",(event)=>{
        console.log("poop")
        boxesList.scrollIntoView()
      })
    }

    let leaseDuration = document.querySelector("#leaseDuration")
    let leasePrice = document.querySelector("#leasePrice")
    let durationSlider = document.querySelector("#duration")
    durationSlider.addEventListener("change", (event)=>{
        leaseDuration.textContent = event.target.value + " месяц(ев)"
        leasePrice.textContent = (parseInt(event.target.value) * parseFloat(modalBoxPrice.dataset.rate)) + " ₽"
    })

    let inputCode = document.querySelector("#code")
    let modalBoxWhAddress = document.querySelector("#boxWhAddress")
    let modalBoxCode = document.querySelector("#boxCode")
    let modalBoxDims = document.querySelector("#boxDims")
    let modalBoxArea = document.querySelector("#boxArea")
    let modalBoxPrice = document.querySelector("#boxPrice")

    function fetch_data(event){
        let id = event.currentTarget.dataset.warehouse

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

            present_boxes = data.boxes

            boxesTable.dataset.current = id
            boxPills = []
            for(let i = 0; i<present_boxes.length; i++){
                let outerContainer = document.createElement("a")
                outerContainer.classList.add("js-box-row", "row", "text-decoration-none", "py-3", "px-4", "mt-5", "SelfStorage__boxlink")
                if(present_boxes[i].area<3)
                    outerContainer.classList.add("js-area-to-3")
                if(present_boxes[i].area<10)
                    outerContainer.classList.add("js-area-to-10")
                else
                    outerContainer.classList.add("js-area-from-10")

                let floorCodeContainer = document.createElement("div")
                floorCodeContainer.classList.add("col-12", "col-md-4", "col-lg-3", "d-flex", "justify-content-center", "align-items-center")
                let floorSpan = document.createElement("span")
                floorSpan.classList.add("SelfStorage_green", "fs_24", "me-2")
                floorSpan.textContent = present_boxes[i].floor + " эт."
                let codeSpan = document.createElement("span")
                codeSpan.classList.add("fs_24")
                codeSpan.textContent = "№"+present_boxes[i].code

                floorCodeContainer.appendChild(floorSpan)
                floorCodeContainer.appendChild(codeSpan)


                let areaContainer = document.createElement("div")
                areaContainer.classList.add("col-6", "col-md-4", "col-lg-3", "d-flex", "justify-content-center", "align-items-center")
                let areaSpan = document.createElement("span")
                areaSpan.classList.add("fs_24")
                areaSpan.textContent = present_boxes[i].area + " м²"

                areaContainer.appendChild(areaSpan)
                

                let dimensionsContainer = document.createElement("div")
                dimensionsContainer.classList.add("col-6", "col-md-4", "col-lg-3", "d-flex", "justify-content-center", "align-items-center")
                let dimensionsSpan = document.createElement("span")
                dimensionsSpan.classList.add("fs_24")
                dimensionsSpan.textContent = present_boxes[i].dimensions + " м"

                dimensionsContainer.appendChild(dimensionsSpan)


                let rateContainer = document.createElement("div")
                rateContainer.classList.add("col-12", "col-lg-3")
                let rateSpan = document.createElement("span")
                rateSpan.classList.add("btn", "my-2", "w-100", "text-white", "fs_24", "SelfStorage__bg_orange", "SelfStorage__btn2_orange", "border-8")
                rateSpan.setAttribute("data-bs-toggle", "modal")
                rateSpan.setAttribute("data-bs-target", "#LeaseModal")
                rateSpan.textContent = present_boxes[i].rate + " ₽"
                rateSpan.dataset.box = i

                rateSpan.addEventListener("click", (event)=>{
                    index = parseInt(event.currentTarget.dataset.box)
                    modalBoxWhAddress.textContent = present_boxes[index].warehouse_city+", "+present_boxes[index].warehouse_address
                    modalBoxCode.textContent = "№"+present_boxes[index].code
                    inputCode.value = present_boxes[index].code
                    modalBoxArea.textContent = present_boxes[index].area + " м²"
                    modalBoxDims.textContent = present_boxes[index].dimensions + " м"
                    modalBoxPrice.textContent = present_boxes[index].rate + " ₽"
                    modalBoxPrice.dataset.rate = present_boxes[index].rate
                    durationSlider.value = 1
                    leaseDuration.textContent = "1 месяц(ев)"
                    leasePrice.textContent = parseFloat(present_boxes[index].rate) + " ₽"
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